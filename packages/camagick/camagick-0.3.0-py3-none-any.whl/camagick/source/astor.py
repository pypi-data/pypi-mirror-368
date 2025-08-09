# Load data, attrs, and meta-information (shapes etc) from array storage
# (e.g. HDF5, Zarr, TIled, ...)

import logging, time, math, random, asyncio, importlib, functools

from camagick.processor import ProcessorBase, SourceBase
from camagick.probe import opcast
from numpy import random as np_rand
from numpy import array, zeros, ones

from camagick.storage.base import probe_kind, find_loader, DatasetUnavailable

logger = logging.getLogger(__name__)

def _split_at_brackets(res):
    # Extracts the part between brackets [...] if it exists
    if res[-1] == ']':
        i = res.rfind('[')
        if i >= 0:
            return res[0:i], res[i+1:-1]
        else:
            raise RuntimeError(f'Missing bracket for {res}')
    return res, None


def _make_slicer(s):
    # Generates a tuple of slice() objects from a string
    # of the form "a:b:c,d:e:f,...", where a,b,c ...
    # are integers. Returns "None" if not possible.
    slicers = []
    try:
        for spec in s.split(','):
            nr = spec.split(':')
            if len(nr) == 0:
                slicers.append(slice(None))
            elif len(nr) == 1:
                slicers.append(int(nr[0]) if len(nr[0])>0 else slice(None))
            elif len(nr) == 2:
                slicers.append(slice(int(nr[0]) if len(nr[0])>0 else 0,
                                     int(nr[1]) if len(nr[1])>0 else -1))
            elif len(nr) == 3:
                slicers.append(slice(int(nr[0]) if len(nr[0])>0 else 0,
                                     int(nr[1]) if len(nr[1])>0 else -1,
                                     int(nr[2]) if len(nr[2])>0 else 1))
            else:
                raise RuntimeError(f'{spec} is not a valid slicer')
        return tuple(slicers)
    except ValueError:
        return None


class Processor(SourceBase):

    def __init__(self,                 
                 url: str,
                 kind: str = 'auto',
                 wait=False,
                 **data):
        '''
        Access array data and metadata in storage.

        Some array formats (specifically Zarr) can be stored in various
        backends like S3, accessed via more complex URL formats (e.g.
        via s3:// or https://...). This processor makes no assumptions
        but simply passes on the parameter to the underlying storage
        backend.

        Args:
            url: Location of the data file or main array.
        
            kind: Which storage backend to use. If this is set to "auto",
              we try to guess which storage that would be. Typically this is
              done by parsing the ending of "location" and comparing it against
              a list of well-known endings ("hdf5", "h5", "zarr", "nx", "n5",
              ...), but as the list of supported formats expands, we tend to
              get more creative. It is advisable to explicitly specify the
              format if in doubt. Currently supported keys "zarr" and "hdf5"
              here.

            wait: if set to `True`, waits if data is unavailable
              (`FileNotFoundError` or `DatasetUnavailable`)

            **data: Data to query. The key here is the name inside `caspy`,
              the value is the path inside the array file. This can point to:
               - a typical dataset (e.g. `/group/subgroup/dataset`), in which case
                 we'll return the data array.
               - a slice of a dataset (e.g. `/group/subgroup/dataset[int:int:int]`
                 in which case we'll return the data of the slice
               - request for shape information (e.g. `/dataset.shape`), in which
                 case we'll return the shape
               - request for attributes of groups or datasets (`/dataset.attrs[key]`
                 or `/group.attrs[key]'), in which case we'll return the
                 corresponding attribute.
               - request for sub-items via a `.keys` suffix (the underlying Python
                 object should support the `.keys()` method)
        '''

        # We expect from all array storage systems to support the following:
        #  - slicing via dataset object dataset[...], dataset[()], ...
        #  - access to groups/subgroups/folders via obj['group/subgroup/dataset']
        #  - access to .attrs for groups and datasets.
        #  - access to dataset shapes via dataset.shape

        self._loader_url = url
        self._loader_kind = kind

        # Prepare the data retrieval. Store a map as:
        # { key: (path, action) }, where "key" is the data name inside caspy,
        # "path" is the object location within the data file, and "action"
        # is a callable that returns the desired data (slicing or attr key)
        self._keys = {}

        # waits if FileNotFoundError or DatasetUnavailable errors encountered
        self._wait = wait
        self._unavailable = None

        
        class _slicer_helper:
            # Helps with delaying slicer to a later point (the actual point
            # is to store the slicing information for later use)
            def __init__(self, *s, attr=None):
                self._sli = s if attr is None else s[0]
                self._attr = attr
            def __call__(self, data):
                if self._attr is None:
                    return data[*(self._sli)]
                else:
                    attr = getattr(data, self._attr)
                    if callable(attr):
                        return attr()[self._sli]
                    else:
                        return attr[self._sli]


        # Build up the request database (self._keys).
        # This is a { tag: (inside_path, reader_proc) } dictionary, where:
        #   - "tag" is the name within CAmagick (as usual)
        #   - "inside_path" is the path within the array storage of
        #     the object we want to read
        #   - "reader_proc" is a callable of the signature proc(obj)
        #     that will return the data, when passed the array object
        #     (i.e. loaded dataset or group object)
        for k,v in data.items():
            base, brk = _split_at_brackets(v)
            if brk is not None:
                # Brackets -- either a slicer, or an attrs key
                sli = _make_slicer(brk)
                if sli is not None:
                    # It's a data slicer.
                    action = _slicer_helper(*sli)
                elif base.endswith('.attrs'):
                    r = base.rfind('.')
                    suffix = base[r+1:]
                    # No slicer, just a string we'll use to get an attribute
                    base = base[:r]
                    action = _slicer_helper(brk, attr=suffix)
                else:
                    raise RuntimeError(f'Invalid slicer for {base}: {brk}')

            else:
                # No brackets -- we return either a shape, or the data
                if base.endswith('.shape'):
                    r = base.rfind('.')
                    suffix = base[r+1:]
                    base = base[:r]
                    action = lambda x: x.shape
                elif base.endswith('.keys'):
                    r = base.rfind('.')
                    suffix = base[r+1:]
                    base = base[:r]
                    action = lambda x: array([k for k in sorted(x.keys())])
                else:
                    action = lambda x: x[()]

            self._keys[k] = (base, action)


    def _get_loader(self, real_url):
        loader_kind = self._loader_kind
        return find_loader(kind=(loader_kind if loader_kind not in (None, 'auto') \
                                 else probe_kind(real_url)))


    def _get_url(self, **params):
        url_fmt = self._loader_url
        real_url = url_fmt.format(**params)
        if not hasattr(self, "_prev_url") or (real_url != self._prev_url):
            logger.info(f'msg="New input URL" url="{real_url}"')
            self._prev_url = real_url
        return real_url


    def read(self, context=None):
        ctx = context if context is not None else {}
        result = {}
        url = self._get_url(**ctx)
        Loader = self._get_loader(url)
        reqd_elements = { k:v[0] for k,v in self._keys.items() }
        with Loader(url, mode=None, **reqd_elements) as df:
            for k,v in self._keys.items():
                action = v[1]
                dobj = df[k]
                result[k] = action(dobj)
        return result


    async def __call__(self, data=None, context=None):    
        return self.read(context)
