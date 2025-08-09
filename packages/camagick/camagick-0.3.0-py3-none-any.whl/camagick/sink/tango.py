#!/usr/bin/python3

import logging, time, math, random, asyncio

from camagick.processor import ProcessorBase, SinkBase
from camagick.probe import opcast

import numpy as np

import tango
from tango import asyncio as tas

logger = logging.getLogger(__name__)

class Processor(SinkBase):
    '''
    Sends data to a tango device
    '''

    def __init__(self, dev: str, **tags):
        '''
        Produces data.

        Args:
            **tags: tag -> tango variable
        '''
        self._dev = dev
        self._tags = tags


    async def startup(self):
        self._proxy = await tas.DeviceProxy(self._dev)
        logger.info(f'msg="Have device proxy" proxy={self._proxy}')


    async def shutdown(self):
        pass


    async def __call__(self, data=None, context=None):

        awaitables = []
        if data is None:
            data = {}
        
        for k in data:
            attr = self._tags[k]
            val = data[k]
            logger.info(f'msg="Setting" device="{self._dev}" attr={attr} value={val}')
            awaitables.append(self._proxy.write_attribute(attr, val))

        await asyncio.gather(*awaitables)
