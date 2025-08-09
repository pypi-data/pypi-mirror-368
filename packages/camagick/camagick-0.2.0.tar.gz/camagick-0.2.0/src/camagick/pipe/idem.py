from camagick.processor import ProcessorBase

class Processor(ProcessorBase):
    '''
    Similar to `--only .*`, i.e. passes on all data tags unfiltered.
    '''
    async def __call__(self, data=None, context=None):
        return data
    
