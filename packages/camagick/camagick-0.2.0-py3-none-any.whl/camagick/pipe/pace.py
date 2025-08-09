
from camagick.processor import ProcessorBase

import logging, time, asyncio

logger = logging.getLogger(__name__)

class Processor(ProcessorBase):

    def __init__(self, Hz: float = None, ms: float = None, s: float = None):
        '''
        Slows down processing speed by the specified rate or period length.
        '''
        if Hz is not None:
            self._period = 1.0/Hz
        elif ms is not None:
            self._period = ms / 1000.0
        elif s is not None:
            self._period = s

        self._last_run = 0


    async def startup(self):
        pass


    async def shutdown(self):
        pass


    async def __call__(self, data=None, context=None):

        diff = (time.time()-self._last_run)
        
        if self._period > diff:
            await asyncio.sleep(self._period-diff)

        self._last_run = time.time()
            
        return data
