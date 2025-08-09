
from camagick.processor import ProcessorBase

import logging, time, asyncio, re
import numpy as np

logger = logging.getLogger(__name__)

class Processor(ProcessorBase):
    '''
    Allow only non-empty datasets to pass
    '''
    async def __call__(self, data=None, context=None):
        return {
            k:v for k,v in filter(lambda x: len(x[1].flatten())>0,
                                  data.items())
        }
