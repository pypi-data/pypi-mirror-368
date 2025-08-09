
from camagick.processor import ProcessorBase

def populate_argparser(parser):
    pass

class Processor(ProcessorBase):
    '''
    Changes the array shape of the input data.
    '''
    
    def __init__(self, *dims, shape=None, **kw):
        super().__init__(**kw)
        if len(dims)==0:
            self.shape = shape
        else:
            self.shape = dims

    async def __call__(self, data=None, context=None):
        #shape = (context.get(f'{k}_shape', self.shape) for k in data) \
        #    if context is not None else self.shape
        shape = self.shape
        
        if shape is None:
            raise RuntimeError(f'msg="{self.__class__.__name__} requires a shape '
                               f'for {k} got none"')

        return { k:v.reshape(shape) for k,v in data.items() }
