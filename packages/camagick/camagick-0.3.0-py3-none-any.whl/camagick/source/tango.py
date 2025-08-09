#!/usr/bin/python3

import logging, time, math, random, asyncio

from camagick.processor import ProcessorBase, SourceBase
from camagick.probe import opcast

import numpy as np

import tango
from tango import asyncio as tas

logger = logging.getLogger(__name__)

class Processor(SourceBase):
    '''
    Reads data as a tango client, from tango variables
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

        if data is None:
            data = {}

        awaitables = [ self._proxy.read_attribute(self._tags[k]) for k in self._tags ]
        result = await asyncio.gather(*awaitables)

        my_data = {
            k:np.array(r.value) for k,r in zip(self._tags, result)
        }

        #my_data.update(data)

        return my_data
