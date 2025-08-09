from camagick.source.astor import Processor as ProcessorBase
import zarr

def open_data_file(path):
    return zarr.open_group(path, 'r')

class Processor(ProcessorBase):
    '''
    Short for `--astor kind=zarr`.
    '''
    def __init__(self, url: str, **data):
        super().__init__(url, kind='zarr', **data)
