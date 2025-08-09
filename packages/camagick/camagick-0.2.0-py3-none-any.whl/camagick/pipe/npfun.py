from camagick.processor import ProcessorBase
import numpy as np

def _lucky_parser(s):
    
    if s == 'None':
        return None

    if s in ('False', 'false'):
        return False

    if s in ('True', 'true'):
        return True

    for t in [ int, float ]:
        try:
            return t(s)
        except ValueError:
            continue

    return s


class Processor(ProcessorBase):
    '''
    Numpy-based single-array operations (mean, average, max, ...)

    Essetially, this processor will call the named operation on
    every input dataset, and replace the data with the result of
    the operation.

    Hint: you may want to use the `--rename` processor right after
    this one, and in conjunction with a suitable combination of
    fanout / chain flow control, if you intend to keep both data sets.

    Example:

      caspy ... { [ --only .* ]
                  [ --npstat1 sum --rename {}_sum ] } ...

    This will calculate the sum of incoming data, and pass on the
    sum as {}_sum, as well as the original data. (The latter part is
    owing to the fact that we've enclosed the operations in a fanout
    structure.)
    '''

    def __init__(self, op: str, **args):
        '''
        Args:
            op: operation to use (as string, as available in the numpy namespace).
              Any operation is allowed that uses (a) a single array as its first
              input parameter, and (b) only parameters that can be named as its
              further parameters.
        
            **args: named arguments to pass on as the operation's parameters after
              the array.
        '''
        self.stat_proc = getattr(np, op)

        # This will fail because most 'args' values will be strings,
        # and we need to translate them to useful python types
        # (True, None, int(...), ...)
        self.stat_kwargs = { k:_lucky_parser(v) for k,v in args.items() }
    
    async def __call__(self, data=None, context=None):        
        return {
            k:self.stat_proc(v, **self.stat_kwargs) \
            for k,v in data.items()
        }
    
