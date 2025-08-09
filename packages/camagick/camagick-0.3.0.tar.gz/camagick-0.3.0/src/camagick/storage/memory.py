from camagick.storage.base import ArrayAccess as ArrayAccessBase
from camagick.storage.base import RefuseIndex, RefuseOverwrite, RefuseSparse

import numpy as np
import h5py, logging, os

logger = logging.getLogger(__name__)

class _MemoryArrayRepo:
    def __new__(cls, *a, **kw):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls, *a, **kw)
        return cls._instance

    def __init__(self):
        self._storage = {}


class ArrayAccess(ArrayAccessBase):
    '''
    Implementation of an array store that holds all the data in memory.

    This is mainly for debugging and testing purposes, but might be
    useful. Stores the data in a number of stacked dict() containers
    -- one for each level (starting wiht '/'), and the datasets as numpy
    arrays.
    '''

    class _dset_wrapper:
        # This is needed because Numpy arrays are difficult to
        # resize in-place. We hold one level of indirection so
        # that no other instance references the actual array.
        def __init__(self, ar):
            self._ar = ar

        @property
        def shape(self):
            return self._ar.shape

        @property
        def dtype(self):
            return self._ar.dtype

        def __setitem__(self, *a):
            return self._ar.__setitem__(*a)

        def resize(self, new_shape):
            self._ar.resize(new_shape)

        def __repr__(self):
            return self._ar.__repr__()
        

    def __init__(self, store=None, sdir=None, mode=None, **tags):
        self._repo = _MemoryArrayRepo()
        super().__init__(store, sdir, mode, **tags)

    def _resize_dataset(self, dset, new_shape):
        dset.resize(new_shape)

    def _open_writable(self, store):
        return self._repo._storage.setdefault(store, {})

    def _close(self, tag):
        pass

    def _ensure_dataset_base(self, stor, dset, **attrs):
        d = stor
        parts = dset.split('/')
        for c in parts[:-1]:
            d = d.setdefault(c, {})
        return d, parts[-1]

    def _ensure_dataset(self, path, base, dtype=None, frame_shape=None, **attrs):
        parts = path.split('/')
        name = parts[-1]
        if len(name) == 0:
            raise RuntimeError(f'bad dataset: {name}')
        if len(parts) > 1:
            for c in parts[:-1]:
                base = base[c]
                
        if parts[-1] in base:
            d = base[parts[-1]]
            if (not self.readonly) \
               and ((d.dtype != dtype) or \
                    (d.shape[1:] != frame_shape)):
                raise RuntimeError(f'incompatible array {d.dtype}/{d.shape[1:]}')
            return d
        elif not self.readonly:
            d = base[parts[-1]] = self._dset_wrapper(
                np.ndarray((0, *frame_shape), dtype=dtype)
            )
            return d
        else:
            raise RuntimeError('read-only array')
        
