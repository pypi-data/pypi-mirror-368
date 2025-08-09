from camagick.source.astor import Processor as ProcessorBase
import h5py

def open_data_file(path):
    return h5py.File(path, 'r')

class Processor(ProcessorBase):
    '''
    Short for `--astor kind=hdf5`.
    '''
    def __init__(self, url: str, **data):
        super().__init__(url, kind='hdf5', **data)
