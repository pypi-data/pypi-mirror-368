from camagick.processor import ProcessorBase
import numpy as np


class Processor(ProcessorBase):    
    '''
    Introduces a new axis (time) and stacks data along it.

    The processor keeps a copy of all historical data of
    a particular tag, up to `size` (see initialization) number
    of data points. It acts as a ring buffer, i.e. once the
    maximum number of points is reached, new older points get
    discarded as newer ones are added.
    '''

    def __init__(self, size: int = 128, reslice: bool = True):
        '''
        Args:
            size: number of points to keep stacked. Older points
              get discarded as newer ones are added.

            reslice: scalar values and 1D arrays with a single element
              are sometimes used interchangably in Caspy. Usually this
              isn't a problem, but here it becomes one: stacking scalars
              results in a 1D array (which can be easily plotted), while
              stacking a 1D / single element array results in a 2D array
              (with the 2nd dimension of size 1), which *cannot* be plotted
              and must be either sliced, or treated as an image.

              Setting this to True is a convenience option to actually
              do the reslicing on the fly in such cases.

              Default is True.
              
        '''

        self._ring_size = size
        self._stacks = {}
        self._reslice = reslice
        
    
    async def __call__(self, data=None, context=None):

        if data is None:
            return None

        for tag, inp in data.items():
            stack_shape = (self._ring_size, *inp.shape)
            try:
                prev = self._stacks[tag]
            except KeyError:
                prev = np.ndarray(stack_shape)
                prev[...] = inp.mean()

            cur = self._stacks[tag] = np.roll(prev, -1, 0)
            cur[-1] = inp

        output = {}

        for k in data:
            stk = self._stacks[k]
            if len(stk.shape) == 2 and stk.shape[1] == 1 and self._reslice:
                output[k] = stk[:,0]
            else:
                output[k] = stk
            
        return output
