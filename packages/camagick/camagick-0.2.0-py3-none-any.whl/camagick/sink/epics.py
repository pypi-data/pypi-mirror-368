from camagick.processor import ProcessorBase, SinkBase
import numpy as np
from caproto.asyncio.client import Context
from caproto import ChannelData
from contextlib import suppress

import logging, asyncio

logger = logging.getLogger(__name__)


class Processor(SinkBase):
    def __init__(self, **targets):
        '''
        Writes data to existing EPICS PVs.
        
        Args:
            **targets: key-value pairs of data tags -> full PVs
              where to write each of the datasets.
        '''
        self._targets = targets


    async def startup(self):
        self._ctx = Context()
        tmp = await self._ctx.get_pvs(*[v for k,v in self._targets.items()])
        self._pvs = { k:v for k,v in zip(self._targets,tmp) }
        self._errors = { k:None for k in self._targets }


    async def shutdown(self):
        await self._ctx.disconnect()


    def _maybe_log_error(self, tag, msg):
        e = self._errors.get(tag, None)
        if e is None:
            logger.error(f'msg="Data error, future erros will be silenced" '
                         f'detail="{msg}" tag={tag}')
        self._errors[tag] = e


    def _maybe_clear_error(self, tag):
        if len(self._errors):
            self._errors[tag] = None
            logger.info(f'msg="Available again" tag={tag} pv={self._targets[tag]}')
        

    async def __call__(self, data=None, context=None):
        '''
        Writes data to their corresponding PVs if there's
        a PV waiting.
        '''

        set_list = []

        for tag,pv in self._pvs.items():
            val = data.get(tag, None)
            if val is None:
                self._maybe_log_error(tag=tag, msg=f'Tag not available')
                allowed_tags = ','.join([k for k in data])
                self._maybe_log_error(tag=tag, msg=f"Options: {allowed_tags}")
                continue
            set_list.append(pv.write(val))

        exc = await asyncio.gather(*set_list, return_exceptions=True)

        for t,e in zip(self._pvs, exc):
            if isinstance(e, Exception):
                self._maybe_log_error(t, e)
            else:
                self._maybe_clear_error(t)

        return {
            k:v for k,v in filter(lambda x: x[0] not in self._pvs,
                                  data.items())
        }
