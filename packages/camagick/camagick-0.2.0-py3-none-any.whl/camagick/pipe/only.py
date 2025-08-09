
from camagick.processor import ProcessorBase

import logging, time, asyncio, re
import numpy as np

logger = logging.getLogger(__name__)

class _FilterBase(ProcessorBase):
    # We're going to use this for both whitelist and blacklist
    # based filtering, but the blacklist one is named 'except'
    # and located elsewhere.
    
    def __init__(self, allow, *items):
        self._list = [ re.compile(i) for i in items ]
        self._allow = allow

    async def startup(self):
        pass

    async def shutdown(self):
        pass

    async def __call__(self, data=None, context=None):
        matcher = lambda x: np.array([
            ((l.match(x[0]) is not None) == self._allow) for l in self._list
        ]).any()
        
        return { k:v for k,v in filter(matcher, data.items()) }


class Processor(_FilterBase):
    '''
    Whitelist-based data blocker -- allows only named data to pass.

    Allows only data items to pass with keys that match any
    of the regex expressions. The match is case-sensitive.
    '''
    def __init__(self, *items: list):
        super().__init__(True, *items)
    
