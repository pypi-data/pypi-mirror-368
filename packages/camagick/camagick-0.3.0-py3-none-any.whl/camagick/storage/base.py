'''
Array Storage API abstraction

This is meant to implement the operations that CAmagick supports in
an backend-agnostic way. Typically, CAmagick writes to HDF5, Zarr
and Tiled. So this API intents to support the common denominator of
all of these:

- Eternal / internal path (i.e. an entry point, "file" or "url"
  that designates a high-level resource, and an internal path
  that designates a low-level resource within the high-level
  one)

- Groups or Datasets (HDF5-like hiearchical structure, where
  there are datasets or groups, with the groups containing further
  datasets or subgroups, accessible by ["...path..."])

- Datasets can be sliced, and meta information (in particular data type
  and shape) can be accessed by `.dtype`, respectively `.shape`

- Datasets and/or groups can have attributes by means of `.attrs[...]`

- Files can be opened for reading, or for read-writing, optionally
  overwriting or refusing to create new files when opening for
  read-writing and the file already exists / doesn't exist.
'''

import time, logging, numpy, functools, asyncio, importlib

logger = logging.getLogger(__name__)

__all__ = [
    "RefuseIndex",
    "RefuseOverwrite",
    "RefuseSparse",
    "ArrayAccess",
    "MemoryArrayAccess"
]

# list of procedures that return True if a specific storage
# path/url is of a specific format.

_format_probe = {
    'hdf5': lambda x: numpy.array([
        x.endswith(s) for s in \
        ('.h5', '.hdf', '.hdf5', '.nx', '.cdf4')
    ]).any(),
    
    'zarr': lambda x: numpy.array([
        x.endswith(s) for s in \
        ('.z', '.zarr')
    ]).any(),
}

def probe_kind(url):
    for kind, stest in _format_probe.items():
        if stest(url):
            return kind
    raise RuntimeError(f'no matching loader found for {url}')

def find_loader(url=None, kind=None):
    if kind is None:
        kind = probe_kind(url)
    mod = importlib.import_module(f'camagick.storage.{kind}')
    return getattr(mod, 'ArrayAccess')


class RefuseIndex(RuntimeError): pass

class RefuseOverwrite(RefuseIndex): pass

class RefuseSparse(RefuseIndex): pass

class DatasetUnavailable(RuntimeError):
    def __init__(self, tag, reason=None):
        self.tag = tag
        super().__init__(f'Dataset unavailable: "{tag}" ({reason})')

class ArrayAccess:
    '''
    This is just to document the abstract API.

    The API elements are heavily tailored towards CAmagick's needs, which
    are essentially appending new data ("frames") to existing datasets.
    To implement a new backend, at least the following members need
    to be defined:

    - Store opening: `_open_writable()`
    - Dataset management: `_ensure_dataset_base()`, `_ensure_dataset()`

    Additonally, possibly:
    - Read-only access: `_open_readable()` if different from read-write access
    - Store closing: `_close()`, if the store object doesn't support `.close()`    
    - Dataset sizing: `._resize_dataset()` (and possibly `_reset_dataset()`),
      if the dataset doesn't have a `.resize(shape)` function.
    '''

    def __init__(self, store=None, sdir=None, mode=None, **tags):
        '''
        Initializes the storage mechanism.

        This is typically created by higher layers, once per session (i.e.
        read/write loop run). Saving to multiple locations (i.e. store "files"
        paths within files) is supported by virtue of appropriate combination
        of `sdir` and/or `**tags` parameters. The actual storage backend objects
        are created lazily, during async enter/exit environments. This makes it
        possible to use formatting spec `{...}` in the storage paths, and
        set those paths at a later time using format keys.
        
        
        Args:
            store: Top-level store path (file name or URL). May contain
              formatting values `{...}`, which are evaluated later at
              `.push_frame()` time.

            sdir: Path inside the store. If this is not `None`, it is
              prepended to any of the tags logation from `tags`. It is
              intended to make it easy to specify a top-level directory,
              or to make a one-size-fits-all path spec for all tags.
              May contain formatting values `{...}`, which are evaluated
              at `.push_frame()` time.

            mode: What to do when we're required to create or overwrite a
              data point. We only concert ourselves with data points since
              this is what CAmagick's basic data currency is. For everything
              else (files, groups), the policy follows whatever must be done
              to ensure the data point mode policy can be followed.
        
              This must be either `None`, or a string consistinc or a
              combination of `a` (append), `o` or `O` (overwrite)
              or `x` (reset), possibly in combination with `+` (top-up),
              meaning:
        
                 - `a`: require that the data point be always appended
                   to the current dataset -- never overwrite or delete
                   existing data.
        
                 - `o`: overwrite already existing data points (frames).
                   If the shape of the new data point frames doesn't match
                   the old ones, then fail.

                 - `O`: same as `o`, but additioally delete and re-create
                   whole dataset entries, if the shape or data type of the
                   existing dataset does not match the new request.

                 - `x`: reset the entire dataset (i.e. delete all existing
                   data points) if a data point already exists at the
                   specified index.

                 - `+`: top-up marker will fill up empty slots, but without
                    actually writing any data to them. They will remain
                    filled with default settings of the corresponding backend
                    and the data type. If top-up is not specified, otherwise
                    the operation will fail if index is higher than the one of
                    the next slot in turn.

              If `mode` is set to `None`, each dataset, and consequently the
              whole store, is opened for reading only. This also reflects
              the behavior of the async environment enter/exit functionality.

            **tags: Keys are tag names (by which to refer the data in
              `.push_frame()`, and values are path elements, for each
              frame in itself. If the values are `None`, the value of `sdir`
              is used. Otherwise the value of `sdir` (if itself not `None`)
              is prepended to the path values.
        '''
        self._stor_spec = (store, sdir)
        self._stor_dspath = {
            k:(sdir if sdir is not None else '')+(v if v is not None else '') \
            for k,v in tags.items()
        }
        self._stor_timeout = 1.0
        self._refcnt = 0
        self._frame_mode = mode
        #self._stor_keys = {}

    
    #self._stor_keys = kw.copy()


    @property
    def readonly(self):
        return self._frame_mode is None


    def __prepare_stor_open(self):
        if self._frame_mode is None:
            self._stor_open = functools.partial(self._open_readable)
        else:
            self._stor_open = functools.partial(self._open_writable)




    # Typically we are accessing several _arrays_ from one _file_
    # (or from a smaller number of files). We can't close files
    # or generally file-like handles (sockets) as long as there
    # are still arrays using it. So we need to implement a
    # file-open caching refcounter.
    # This holds the final store path (i.e. "file path") as known
    # to us as key, and the store refcounter (see ._open()) as value.
    # So this is where first part of the magic happens: we store
    # a StorObj for every data tag we want to save. We don't
    # have any of the tags available here, but we initialize
    # the cache and store the keys.
            
    def __sync_open_paths(self, paths):
        objlist = [
            self.__open_store(k, timeout=self._stor_timeout) \
            for k in paths
        ]
        return { k:v for k,v in zip(paths, objlist) }        

    #def __async_open_paths(self, paths):
    #    objlist = await asyncio.gather(
    #        *[self.__async_open_store(k, timeout=self._stor_timeout) \
    #          for k in paths],
    #        return_exceptions=False
    #    )
    #    return { k:v for k,v in zip(paths, objlist) }


    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, *args):
        self.__exit__()

    def __enter__(self):
        self._refcnt += 1        
        if self._refcnt > 1:
            return self
        self.__prepare_stor_open()
        self._stor_obj = self.__sync_open_paths(self._stor_dspath)
        return self

    def __exit__(self, *args):
        self._refcnt -= 1
        if self._refcnt < 0:
            raise RuntimeError('you are not supposed to be here')
        for k,o in self._stor_obj.items():
            self.__close_store(obj=o)
        self._stor_obj = None
    


    class StorRefcnt:
        ## Store base object ("file")
        fo = None

        ## When this reaches 0 again, we can close .fo
        refcnt = 0

        def __init__(self):
            pass


    class StorObj:
        
        ## Refcounter object for the store "file" object
        fref = None

        ## Base object for dataset (whether this is
        ## "file" or "group", backend specific)
        bo = None

        ## Dataset path inside the storage
        dpath = None


        def __init__(self):
            pass


    def __open_store(self, tag, timeout=1.0):
        # Generic (backend-agnostic) store open(). This is calle per _tag_,
        # i.e. possibly multiple times per storage backend. We have a pretty
        # confusing refcount system to ensure that every backend is opened
        # only once, and closed when the last dataset is being discarded.

        self._stor_fileobj = {}        
        
        obj = self.StorObj()
        stor = self._stor_spec[0]
        path = (self._stor_spec[1] if self._stor_spec[1] is not None else '') + \
            self._stor_dspath.get(tag, '')

        # Some storage backends have locks which make opening operations
        # fail temporarily. Try several times until a final timeout.
        # The "file" here will stay open and needs to be closed with
        # `._close(tag)`. At API level, use aenter/aexit!

        # Find the storage backend first
        try:
            # Store backend already open -- reuse
            fref = self._stor_fileobj[stor]
            fref.refcnt += 1

        except KeyError:
            # Store backend needs to be opened first
            fref = self._stor_fileobj[stor] = self.StorRefcnt()
            fref.refcnt = 1
            fref.fo = self._stor_open(stor)

        try:
            obj.fref = fref
            obj.bo, obj.dpath = self._ensure_dataset_base(obj.fref.fo, path)
            return obj

        except Exception as e:
            err = f'msg="Cannot ensure base of dataset" dset={tag} reason="{e}"'
            logger.error(err)
            self.__close_store(obj=obj)
            raise DatasetUnavailable(tag, err)


    def _open_readable(self, store):
        self._open_writable(store) # default implementation


    def _open_writable(self, store):
        raise RuntimeError('not implemented')


    def _close(self, stor_obj):
        '''
        Closes the store object referenced by `stor_obj`.
        The default implementation just calls a `.close()` if it finds one,
        because that's what most file or socket based backends would do.
        You may need to reimpement this.
        '''
        stor_obj.close()
        

    def __close_store(self, tag=None, obj=None):
        # FIXME: check that every file is closed only _once_,
        # even if there are several tags that point to the
        # same file!
        if obj is None:
            obj = self._stor_obj[tag]

        if obj.fref.refcnt <= 0:
            # This is a bug
            raise RuntimeError(f'double-close for "{tag}"?')

        obj.fref.refcnt -= 1

        if obj.fref.refcnt == 0:
            self._close(obj.fref.fo)

            
    def _split_dset_path(self, dset_path, splitter='/'):
        # Helper that will return the (node path, dataset path)
        # out of a whole path.
        # If there's only one component, assume it's a dataset.
        parts = dset_path.split(splitter)
        
        if len(parts) == 0:
            raise RuntimeError(f'invalid dataset path {dset_path}')

        if len(parts) == 1:
            return ('', parts[0])

        return ('/'.join(parts[:-1]), parts[-1])
               


    def _ensure_dataset_base(self, stor, dset, **attrs):
        '''
        Makse sure the base for storing the dataset exists.

        Args:
            stor: The storage object (file or group)
        
            dset: Dataset path relative to `stor`
        
            **attrs: ?

        Returns a `(baseobj, dset_path)` tuple. `dset_path` here needs
        to be relative to `baseobj`.
        '''
        raise RuntimeError('not implemented')


    def _ensure_dataset(self, path, base, dtype=None, frame_shape=None, **attrs):
        '''
        Ensure the existence of the target dataset.
        
        This is typically called with the first received frame-push (i.e.
        data point), and is intended to set sets names, types,
        attributes etc.

        Args:
            base: where to put the dataset; for some storage backends
             this is "file" object, for others this is the group object
             that immediately holds the dataset

            path: full path of the dataset inside `base`
        
            dtype: data type (numpy-dtype); if array is in read-only
              mode, this and `frame_shape` are expected to be `None`,
              and the actual data type and frame shape of the target
              object will be ignored.
        
            frame_shape: shape of the data point; note that
              the actual shape of the resulting data set will contain
              one extra dimension upfront (i.e. the frame index).
        
            *attrs: dataset attributes

        Return the dataset object.
        '''
        raise RuntimeError('not implemented')


    def _resize_dataset(self, dset, new_shape):
        '''
        Helper for `._ensure_frame()`.

        Essentially, this is the implementation-dependent part. Most backends
        will simply offer a `.resize()` call (this is true for HDF5 and Zarr),
        which is also the default implementation here.

        But others may require a more elaborate procedure (e.g. saving data,
        resizing, restoring).
        '''
        dset.resize(new_shape)


    def _reset_dataset(self, dset):
        '''
        Helper for `._ensure_frame()`.

        Erases all data points from a dataset.
        '''
        new_shape = [int(i) for i in (0, *(dset.shape[1:]))]
        self._resize_dataset(dset, new_shape)


    def _ensure_frame(self, dset, index):
        '''
        Ensures that `dset` has at least `index` points in its first dimension.

        Args:
            dset: Dataset object, dependent on the backend

            index: An integer counting the objects (starting with 1?)

        '''
        idiff = (index-dset.shape[0]) + 1

        if idiff == 1:
            shape_diff = 1
            
        elif idiff > 1:
            if '+' in self._frame_mode:
                shape_diff = idiff
            else:
                raise RefuseSparse(f'msg="Sparse writing requires top-up flag" '
                                   f'index={index} frames={dset.shape[0]} ')
            
        elif idiff <= 0:
            if 'a' in self._frame_mode: # append mode
                raise RefuseOverwrite(f'msg="Overwrite not permitted" index={index} '
                                      f'frames={dset.shape[0]} dataset="{dset.name}" '
                                      f'file=""')

            elif 'o' in self._frame_mode or 'O' in self._frame_mode: # overwrite mode
                shape_diff = 0

            elif 'x' in self._frame_mode: # reset mode
                logger.info(f'msg="Resetting dataset" index={index} '
                            f'frames={dset.shape[0]} dataset="{dset.name}"')
                self._reset_dataset(dset)

                shape_diff = index+1

            else:
                raise RuntimeError(f'BUG: No shape diff for mode: {self._frame_mode}')

        if shape_diff > 0:
            new_shape = [int(i) for i in (dset.shape[0]+shape_diff, *(dset.shape[1:]))]
            logger.debug(f'msg="Resizing dataset" '
                         f'size={dset.shape[0]} '
                         f'index={index} diff={shape_diff} idiff={idiff} '
                         f'shape={new_shape}')
            self._resize_dataset(dset, new_shape)


    async def push_frame(self, index, **data):
        '''
        Received for every data point in a scan.

        Args:
            index: Integer to determine the position of the current
              data point in the overall (larger) dataset. This should
              always point to the next available index in the first
              dimention, i.e. if the existing dataset has dimension
              (37, N, M), with the current data point to become
              the 38th, then `index` needs to be 37 (counting starts
              at 0).

              Behavior if the index doesn't match the shape is defined
              by the class-global parameter `mode`.

              If this is `None`, the next free slot (i.e. current_size+1)
              is used, essentially making the operation always succeed
              as if "append" mode were active.

              If this is a negative number (e.g. -1) and the dataset
              doesn't exist, it is created according to shape
              specification of the input data, but with length 0
              (i.e. no points are copied).
              
            **data: dictionary from data name ("tag") to data arrays
        '''

        for key,container in data.items():
            obj = self._stor_obj[key]
            dset = self._ensure_dataset(obj.dpath,
                                        obj.bo,
                                        container.dtype,
                                        container.shape)

            if index is None:
                index = container.shape[0]

            if index >= 0:
                self._ensure_frame(dset, index)
                item = numpy.array(container)
                dset[index] = item


    def __getitem__(self, tag):
        '''
        Returns a handle to the object internally known as `tag`, according
        to the path spec specified at `__init__` time. This is generally
        supposed to be a dataset.
        '''
        obj = self._stor_obj[tag]
        return self._ensure_dataset(obj.dpath, obj.bo)
