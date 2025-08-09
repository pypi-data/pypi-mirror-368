from camagick.storage.base import ArrayAccess as ArrayAccessBase
from camagick.storage.base import RefuseIndex, RefuseOverwrite, RefuseSparse

import numpy as np
import h5py, logging, os

logger = logging.getLogger(__name__)    

class ArrayAccess(ArrayAccessBase):
    '''
    Implementation of a HDF5 file array access.
    '''

    def __init__(self, store=None, sdir=None, mode=None, **tags):
        super().__init__(store, sdir, mode, **tags)

        
    def _open_writable(self, store):
        self.__ensure_directory_of(store)
        return h5py.File(store, 'a')


    def _open_readable(self, store):
        return h5py.File(store, 'r')


    def __ensure_directory_of(self, path):
        # Makes sure all path components up to the HDF5 file name exist
        print('dir of:', path)
        d = os.path.dirname(path)
        if (len(d) > 0):
            if not os.path.exists(d):
                os.makedirs(d)
                return
            if (not os.path.isdir(d)):
                raise RuntimeError(f'msg="Path is required to be a folder" '
                                   f'path="{d}"')


    def _ensure_dataset_base(self, stor, dset, **attrs):
        # Makes sure `nodepath` exists in the current h5 file and is a data group
        nodepath, dsetonly = self._split_dset_path(dset)
        subpath = ""
        subnode = stor
        for current in nodepath.split('/'):

            if len(current) == 0:
                continue # nothing to do
            try:
                subnode = subnode[current]
                
            except KeyError:
                logger.info(f'msg="Creating node" file="{subnode.filename}" '
                            f'parent="{subnode.name}" '
                            f'name="{current}"')
                subnode = subnode.create_group(current)

        return (subnode, dsetonly)


    def _dtype_spec_to_dtype(self, ds):
        if isinstance(ds, str):
            try:            
                return {
                    'number': float,
                    'integer': int,
                    'array': float,
                }[ds]
            except KeyError:
                errmsg = f'tag="{key}" msg="Don\'t know how to save" dtype="{dt_spec}"'
                logger.error(errmsg)
                raise RuntimeError(errmsg)

        else:
            return ds


    def _ensure_dataset(self, path, base, dtype=None, frame_shape=None, **attrs):
        '''
        Received with the first data point, sets names, types etc.

        Args:
            name: name or path of the dataset        
            base: HDF5 group object to contain the dataset
            dtype: data type (numpy-dtype)
            point_shape: shape of the data point; note that
              the actual shape of the resulting data set will contain
              more dimension
        '''

        if self.readonly:
            return base[path] if len(path) > 0 else base
        
        dshape = (0, *frame_shape)
        
        try:
            dset = base[path]

            if (dset.dtype != dtype):
                if  'O' not in self._frame_mode:
                    raise RuntimeError(f'msg="Dataset exists with different dtype"'
                                       f'have="{dset.dtype}" want="{dtype}"')
                else:
                    del base[path]
                    raise KeyError()

            if dset.shape[1:] != dshape[1:]:
                if  'O' not in self._frame_mode:                
                    raise RuntimeError(f'msg="Dataset exists with different shape"'
                                       f'have="{dset.shape}" want="{dshape}"')
                else:
                    del base[path]
                    raise KeyError()

        except KeyError:
            logger.info(f'msg="Creating dataset" file="{base.file.filename}" name="{path}" '
                        f'shape="{dshape}" dtype={dtype}')
            dset = base.create_dataset(path, dshape, maxshape=(None, *dshape[1:]),
                                       dtype=dtype, compression='lzf')

        return dset

