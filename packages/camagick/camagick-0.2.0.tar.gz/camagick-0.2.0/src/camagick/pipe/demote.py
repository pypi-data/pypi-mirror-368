
from camagick.processor import ProcessorBase

import logging

class Processor(ProcessorBase):
    '''
    Demotes the specified data labels into the context status.
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
            else data.keys()
        
        data_without_labels = { k:data[k] for k in filter(lambda x: x not in lbl, data) }

        context.update({ k:data[k] for k in filter(lambda x: x in lbl, data) })

        return data_without_labels
