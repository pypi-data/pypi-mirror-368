#!/usr/bin/python3

import logging, time, math, random, asyncio

from camagick.processor import ProcessorBase, SourceBase
from camagick.probe import opcast
from numpy import random as np_rand
from numpy import array, zeros, ones

import numpy as np

logger = logging.getLogger(__name__)

class Processor(SourceBase):
    '''
    Produces data from scratch by various means.
    '''

    def __init__(self, method: str, *scalars: str, rate: float = 100.0, opts: dict = None, **arrays):
        '''
        Produces data.

        Args:
            method: string designating the data-producer method.
              currently the following are supported:
                - "sinus" (start, stop, ampl, freq)
                - "random"
                - "zeros"
                - "ones" (factor)
                - "linspace" (start, stop, endpoint)
                - "counter" (start, inc)

            *scalars: list of data tags for scalar values

            rate: Call rate limiter in Hz.

            **arrays: tag -> length map for non-scalar values
        '''

        self._method = getattr(self, f'_make_{method}')
        self._scalars = scalars
        self._arrays = arrays
        self._opts = opts if opts is not None else {}

        self._last_time = 0.0
        self._period = 1.0 / rate

        super().__init__()


    def _make_random(self, shape, **kw):
        return np_rand.random(shape)

    def _make_sinus(self, shape, start=0, stop=6.28, ampl=1.0, freq=1.0):
        return ampl*np.sin(np.linspace(start, stop, shape)*freq)

    def _make_ones(self, shape, factor=1.0):
        return ones(shape)*factor

    def _make_zeros(self, shape, **kw):
        return zeros(shape)

    def _make_linspace(self, shape, start=0.0, stop=1.0, endpoint=True):
        if hasattr(shape, "__len__"):
            if len(shape)>1:
                raise RuntimeError(f'msg="Bad shape for linspace" shape={shape}')
            else:
                num = shape[0]
        else:
            num = shape
        return np.linspace(start, stop, num=num, retstep=False, endpoint=endpoint)

    def _make_counter(self, shape, start=0, inc=1):
        if not hasattr(self, "_cntr"):
            self._cntr = start
        else:
            self._cntr += inc
        return np.ones(shape) * self._cntr


    async def __call__(self, data=None, context=None):

        dwell = min(time.time()-self._last_time, self._period)
        await asyncio.sleep(dwell)
        
        d = {}

        d.update({
            k:self._method(v, **(self._opts)) \
            for k,v in self._arrays.items()
        })

        d.update({
            k:array(self._method([1], **(self._opts))) \
            for k in self._scalars
        })

        return d
