from camagick.processor import ProcessorBase, SinkBase
from camagick.ioc import InstaOutputPVDB, IocServer
import numpy as np
import logging, asyncio, traceback


logger = logging.getLogger(__name__)


class Processor(SinkBase):
    ''' Exports data as EPICS PVs '''

    def __init__(self, prefix=None, suffix=None):
        self.ioc = InstaOutputPVDB()
        self.ioc_prefix = prefix if prefix is not None else ''
        self.ioc_suffix = suffix if suffix is not None else ''
        self.ioc_server = IocServer(self.ioc)
        
        self.pv_format = f'{{prefix}}{{tag}}{{suffix}}'
        logger.info(f'msg="Sink IOC" pv_format="{self.pv_format}"')


    async def startup(self):
        await self.ioc_server.startup()


    async def shutdown(self):
        await self.ioc_server.shutdown()


    async def __call__(self, data=None, context=None):

        if data is None:
            data = {}

        if context is None:
            context = {}

        try:
            await self.ioc.publish_many({
                self.pv_format.format(prefix=self.ioc_prefix, tag=name,
                                      suffix=self.ioc_suffix, **context) : val \
                for name,val in data.items()
            })

        except:
            traceback.print_exc()

        return None
