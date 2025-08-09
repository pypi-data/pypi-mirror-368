from camagick.processor import ProcessorBase, SinkBase
import numpy as np
import zarr, logging, asyncio

logger = logging.getLogger(__name__)

class RefuseIndex(RuntimeError): pass

class RefuseOverwrite(RefuseIndex): pass

class RefuseSparse(RefuseIndex): pass


class ZarrDataStacker:
    '''
    Simple Zarr stacking-based storage.
    '''
    
    def __init__(self, store, group=None, mode=None, zarr_args=None):
        '''
        Args:
            store: Zarr store of where to put the data.
        
            group: Path _inside_ the HDF5 file where to save the data.

            mode: What to do when we're required to save a data point
              in a dataset for which there's already data available
              in the same dataset. See `Processor.__init__()` for documentation
              on available modes.
        '''        
        self._zstore = store
        self._zgroup = group if group is not None else ''
        self._zargs = zarr_args if zarr_args is not None else {}
        self._frame_mode = mode if mode is not None else 'a+'

        logger.info(f'msg="Zarr storage" store="{store}" group="{group}"')


    def _ensure_dataset(self, znode, name, dtype, point_shape):
        '''
        Received with the first data point, sets names, types etc.

        Args:
            znode: Zarr group object
            name: name of the dataset
            dtype: data type (numpy-dtype)
            point_shape: shape of the data point; note that
              the actual shape of the resulting data set will contain
              more dimension
        '''

        dshape = (0, *point_shape)

        fname = str(znode.store_path)
        
        try:
            dset = znode[name]

            if (dset.dtype != dtype):
                if 'O' not in self._frame_mode:
                    raise RuntimeError(f'msg="Dataset exists with different dtype"'
                                       f'have="{dset.dtype}" want="{dtype}" file="{fname}"')
                else:
                    raise KeyError()

            if dset.shape[1:] != dshape[1:]:
                if 'O' not in self._frame_mode:                
                    raise RuntimeError(f'msg="Dataset exists with different shape"'
                                       f'have="{dset.shape}" want="{dshape}" file="{fname}"')
                else:
                    raise KeyError()

        except KeyError:
            logger.info(f'msg="Creating dataset" file="{fname}" name="{name}" '
                        f'shape="{dshape}" dtype={dtype}')
            znode.create_array(name=name, shape=dshape, dtype=dtype, overwrite=True)


    def _ensure_frame(self, dset, index, fname):
        
        idiff = (index-dset.shape[0]) + 1
        
        if idiff == 1:
            shape_diff = 1
            
        elif idiff > 1:
            if '+' in self._frame_mode:
                shape_diff = idiff
            else:
                raise RefuseSparse(f'msg="Sparse writing not allowed; use top-up `+` flag" '
                                   f'index={index} frames={dset.shape[0]} dataset="{dset.name}" '
                                   f'file={fname}')
            
        elif idiff <= 0:
            if 'a' in self._frame_mode:
                raise RefuseOverwrite(f'msg="Overwrite not permitted" index={index} file={fname} '
                                      f'frames={dset.shape[0]} dataset="{dset.name}" '
                                      f'file=""')

            elif 'o' in self._frame_mode or 'O' in self._frame_mode:
                shape_diff = 0

            elif 'x' in self._frame_mode:
                logger.info(f'msg="Resetting dataset" index={index} file={fname} '
                            f'frames={dset.shape[0]} dataset="{dset.name}"')
                new_shape = [int(i) for i in (0, *(dset.shape[1:]))]
                dset.resize(new_shape)

                shape_diff = index+1

            else:
                raise RuntimeError(f'BUG: No shape diff for mode: {self._frame_mode}')

        if shape_diff > 0:
            new_shape = [int(i) for i in (dset.shape[0]+shape_diff, *(dset.shape[1:]))]
            logger.debug(f'msg="Resizing dataset" ' #'file="{dset.group.filename}" '
                         f'name={dset.name} size={dset.shape[0]} '
                         f'index={index} diff={shape_diff} idiff={idiff} '
                         f'shape={new_shape}')
            dset.resize(new_shape)


    def push_data(self, index, **data):
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
              
            **data: dictionary from data name ("tag") to data arrays
        '''

        znode = zarr.open_group(store=self._zstore, path=self._zgroup,
                                mode='a', **self._zargs)

        #print(store, znode)
            
        for key, container in data.items():
            dtype = type(container.flatten()[0].item())
            self._ensure_dataset(znode=znode,
                                 name=key,
                                 dtype=dtype,
                                 point_shape=container.shape)

            dset = znode[key]

            if index is None:
                index = dset.shape[0]

            self._ensure_frame(dset, index, fname=self._zstore)
            item = np.array(container)
            dset[index] = item



class Processor(SinkBase):
    '''
    Saves data as a dataset in a Zarr structure.

    The sink tries to make it easy to obtain uniform, synchronous,
    well-defined arrays of data of the same length. It does so
    mostly by filling up empty frame slots when there isn't any
    data available, or by overwriting data if necessary, according
    to the user specification. This is governed according to the
    `mode` initialization parameter, which determines what to
    do when a dataset already exists.
    '''
    
    def __init__(self,
                 store: str,
                 mode: str = 'a+',
                 index: str = '',
                 strict: bool = True,
                 mt: bool = True,
                 **zarr_args
                 ):
        '''
        Args:
            path: the path format. This is expected to be of the format
              "<file>#<group>/[<dataset>]". The processor splits apart
              the outer part ("<file>") and inner part ("<group>", i.e.
              "inside" the Zarr folder. This isn't of much importance
              when opening already existing zarr groups, but does matter
              if a group doesn't exist yet and needs to be created.
              The splitting is done, as a feature of the Caspy processor,
              at the first '#' character. As such, the '#' character
              never reaches lower Zarr library levels.

              Note that the <file> part is passed directly to
              `zarr.open_group()` as the `store=...` parameter, which means
              that you can make use of Zarr's vast and diverse fs-transparent
              load mechanism by supplying full URLS (e.g. "file:///..." or
              "s3://..." or "http://...").

              If the name of the data set (i.e. "<dataset>") is missing,
              then the store needs to end on "/". In that case, the processor
              will append a dataset name based on the tag.

            mode:  Must be one of `a` (append), `o` (overwrite) or
              `x` (reset), possibly in combination with `+` (top-up):
        
                 - `a`: require that the data point be always appended
                   to the current dataset -- never overwrite or delete
                   existing data.
        
                 - `o`: overwrite already existing data points (frames).

                 - `O`: same as `o`, but additioally delete and re-create
                   whole dataset entries, if the shape or data type of the
                   existing dataset does not match the new request.

                 - `x`: reset the entire dataset (i.e. delete all existing
                   data points) if a data point already exists at the
                   specified index.

                 - `+`: top-up marker will fill up empty slots, but without
                    actually writing any data to them. They will remain
                    filled with default HDF5 settings according  to the data
                    type. If top-up is not specified, otherwise the operation
                    will fail if index is higher than the one of the next
                    slot in turn.
        
            index: name of the context variable which contains the current
              frame index (preferrably integer). If this is an empty string,
              no index is used and essentially every operation is an "append".

            strict: if this is `True` (the default), then any saving errors
              being raised will be allowed to bubble up to the pipe processor.
              Typically, this means the application is being shut down.
              When `False`, then `RefuseIndex` type of errors (typically when
              a frame index is out of place) are being reported, but ignored.

            mt: if set to `True` (the default), writing individual data sets
              to Zarr will happen in parallel, each in its own thread. Given
              that Zarr is built to handle this exact scenario, and we're
              typically writing very small data amounts but with a significant
              amount of API I/O overhead, this is almost always what you want.

            **zarr_args: any arguments to be passed on to `zarr.open_group()`
              for storage.
        '''
        super().__init__()
        
        self._store_fmt = store
        self._store_kw = zarr_args
        self._index_ctx_tag = index
        self._stacker_mode = mode
        self._current_file_and_node = (None, None)
        self._strict = strict
        self._threaded = mt


    def store_inner_split(self, full):
        i = full.find('#')
        if i > 0:
            zfile, zlocal = full[:i], full[i+1:]
        elif i < 0:
            zfile, zlocal = full, '/'
        else:
            raise RuntimeError(f'msg="Don\'t understand path#group combo" store="{full}"')

        return zfile, zlocal


    def group_dset_split(self, inner, default_dset=None):
        l = inner.rfind('/')
        if l < 0:
            raise RuntimeError(f'msg="Cannot determine dataset name from inner path" '
                               f'path="{inner}"')

        node_path = inner[:l+1]
        dset_path = inner[l+1:]

        if len(dset_path) == 0:
            dset_path = default_dset

        return node_path, dset_path


    def get_index(self, context):
        if self._index_ctx_tag not in (None, ''):
            try:
                if self._index_ctx_tag[0] == '@':
                    _index = context[self._index_ctx_tag[1:]]
                else:
                    _index = context[self._index_ctx_tag]
            except KeyError as e:
                err = \
                    f'msg="Index key not available in this frame" ' \
                    f'expected="{self._index_ctx_tag}" ' \
                    f'available="{','.join(context.keys())}"'
                raise RefuseIndex(err)
        else:
            _index = None

        return _index


    def handle_index_error(self, err, tag=None):
        if self._strict or (not isinstance(err, RefuseIndex)):
            raise err
        logger.error(err)
        logger.error(f'msg="Ignoring frame index error as instructed" tag={tag}')

        

    def push_frame(self, tag, cont, index, context, store_fmt, return_exceptions=True):
        full_path = store_fmt.format(tag=tag, **context)
        zfile, zlocal = self.store_inner_split(full_path)
        node_path, dset_path = self.group_dset_split(zlocal, tag)

        try:
            stor = ZarrDataStacker(store=zfile, group=node_path,
                                   mode=self._stacker_mode,
                                   zarr_args=self._store_kw)
            stor.push_data(index=index, **{dset_path: cont})
            return (tag, f'{full_path}[{index}]')
        
        except Exception as e:
            if return_exceptions:
                return e
            else:
                raise e


    async def __call__(self, data=None, context=None):
        
        if data is None:
            data = {}
        if context is None:
            context = {}


        try:
            _index = self.get_index(context)
        except RefuseIndex as e:
            self.handle_index_error(e)
            logger.warning(f'msg="Skipping frame altogether"')
            return


        if self._threaded:
            result = await asyncio.gather(*[
                asyncio.to_thread(
                    self.push_frame, tag, cont, _index, context, self._store_fmt
                ) for tag, cont in data.items()
            ])
        else:
            result = [
                self.push_frame(tag, cont, _index, context, self._store_fmt) \
                for tag, cont in data.items()
            ]

        ret = {}
        for r in result:
            if isinstance(r, Exception):
                self.handle_index_error(r)
            else:
                ret[r[0]] = r[1]

        return ret
