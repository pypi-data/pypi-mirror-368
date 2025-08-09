
from camagick.processor import ProcessorBase

import logging

class Processor(ProcessorBase):
    '''
    Promotes the specified context labels into the data status.
    '''    
    def __init__(self, *labels):
        '''
        Args:
            *labels: explicit list of data labels to demote (case-sensitive)
        '''
        self._labels = labels
    
    async def startup(self):
        pass

    async def shutdown(self):
        pass
    
    async def __call__(self, data=None, context=None):

        lbl = self._labels if (self._labels is not None and len(self._labels)>0) \
            else context.keys()


        nd = data.copy() if data is not None else {}
        for k in lbl:
            try:
                nd[k] = context[k]
                del context[k]
            except KeyError:
                pass

        return nd
