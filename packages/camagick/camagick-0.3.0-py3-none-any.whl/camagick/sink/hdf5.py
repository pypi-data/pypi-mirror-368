from camagick.processor import ProcessorBase, SinkBase
from camagick.storage.hdf5 import ArrayAccess as H5ArrayAccess
from camagick.storage.base import RefuseIndex


import numpy as np
import h5py, logging, os, random, time

logger = logging.getLogger(__name__)

class Processor(SinkBase):
    '''
    Saves data as a dataset in a HDF5 file.

    The HDF5 file / dataset is opened explicitly for each dataset,
    on each run through the pipeline. Files that don't exist are
    created (though not filesystem folders), and files that do
    are appended to (`h5py` mode "a").

    The sink tries to make it easy to obtain uniform, synchronous,
    well-defined arrays of data of the same length. It does so
    mostly by filling up empty frame slots when there isn't any
    data available, or by overwriting data if necessary, according
    to the user specification. This is governed according to the
    `mode` initialization parameter, which determines what to
    do when a dataset already exists.
    '''
    
    def __init__(self,
                 path: str,
                 mode: str = 'a+',
                 index: str = '',
                 strict: bool = True,
                 timeout: float = 0.0,
                 ):
        '''
        Args:
            path: the path format. Generally, the expected syntax is
              "<HDF5-file>#<path-within-file>". The part beyond "#"
              represents the path to the dataset within the HDF5 file.
              The path within file may be just a simple dataset, or may
              contain HDF5 group elements ("#/path/to/group/dataset").
              All groups that don't exist are created.
        
              Note that this is a *format* which will be used for each
              incoming data set, so it should contain at least some
              differentiating element for substitution. Available elements
              are:
                - all the context keys
                - `index` for the designated numeric index of the
                  pipeline run (see `index`)
                - `tag` for the name / tag of the dataset being processed
              
              If the path within HDF5 ends in "/", or is an empty string,
              then it is assumed to be a group, and the format suffix `"{tag}"`
              is automatically assumed.

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

            timeout: If the target HDF5 file is locked, how long to wait for
              unlocking. Default is 5 seconds. Set to 0 to disable waiting,
              in which case a locked file will result in failing to save.
        '''
        super().__init__()
        
        parts = path.split('#')
        
        if len(parts) == 1:
            self.h5file = parts[0]
            self.h5grp = '/{tag}'
        elif len(parts) == 2:
            self.h5file, self.h5grp = parts
        else:
            raise RuntimeError(f'msg="Bad HDF5 path, expected <file>[#<group>[/<dataset>]]" '
                               f'path="path"')

        if (len(self.h5grp)==0) or \
           (self.h5grp[-1]=='/') or \
           self._has_group(self.h5file, self.h5grp):
            self.h5grp += (('/' if self.h5grp[-1] != '/' else '') + '{tag}')

        logger.info(f'msg="Initializing HDF5 saver" file="{self.h5file}" group="{self.h5grp}"')

        self._index_ctx_tag = index
        self._stacker_mode = mode
        self._current_file_and_node = (None, None)
        self._strict = strict
        self._unlock_timeout = timeout


    def _has_group(self, fpath, grp):
        try:
            with h5py.File(fpath, 'r') as h5:
                if isinstance(h5[grp], h5py.Group):
                    return True
        except KeyError: pass
        except OSError: pass
        return False


    def get_index(self, context):
        if self._index_ctx_tag not in (None, ''):
            try:
                if self._index_ctx_tag[0] == '@':
                    _index = context[self._index_ctx_tag[1:]]
                else:
                    _index = context[self._index_ctx_tag]
            except KeyError as e:
                avail = ','.join(context.keys())
                err = \
                    f'msg="Index key not available in this frame" ' \
                    f'expected="{self._index_ctx_tag}" ' \
                    f'available="{avail}"'
                raise RefuseIndex(err)
        else:
            _index = None

        return _index    
        

    def handle_index_error(self, err, tag=None):
        if self._strict or not isinstance(err, RefuseIndex):
            raise err
        logger.error(err)
        logger.error(f'msg="Ignoring frame index error as instructed" tag={tag}')


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
        
        async with H5ArrayAccess(
                store=self.h5file.format(**context), mode=self._stacker_mode,
                **{ k:self.h5grp.format(tag=k, **context) for k in data.keys()}) as stor:
            try:
                await stor.push_frame(_index, **data)
            except RefuseIndex as e:
                self.handle_index_error(e)
