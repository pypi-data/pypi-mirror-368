#!/usr/bin/python3

import logging, asyncio, importlib, traceback

from camagick.processor import ProcessorBase, SourceBase
from camagick.probe import opcast

from ophyd.utils import errors as ophyd_errors
from ophyd import Device, Component
from ophyd.signal import EpicsSignalRO

import numpy as np

import caproto

logger = logging.getLogger(__name__)

class TestDevice(Device):
    # This is just a rapid test object to learn how to
    # deal with multi-component Ophyd devices, what makes
    # them tick, and what do we need to support in "Processor".
    #
    # For this to work, run a test IOC, e.g. like this:
    #
    #   caspy --from-generate random jiffy=100 miffy=100 --to-ioc prefix=foo:
    #
    # Then you can test Ophyd device readout like this:
    #
    #   caspy --from-ophyd camagick.source.ophyd:TestDevice name=foo prefix=foo: --to-plot
    #
    
    miffy = Component(EpicsSignalRO, "miffy")
    jiffy = Component(EpicsSignalRO, "jiffy")

class Processor(SourceBase):
    '''
    Retrieves data from an Ophyd device.

    Examples
    --------

    - Classig `EpicsSignalRO` readout:
      ```
      caspy --from-ophyd ophyd.signal:EpicsSignalRO EXAMPLE:iffy ...
      ```
    '''

    def __init__(
            self,
            cls: str,
            *oa: list,
            mode: str = None,
            opcast: bool = True,
            trigger: bool = False,
            stage: str = "never",
            **ookw: dict
    ):
        '''
        Initializes an Ophyd device from a user-specified module.

        It retrieves all the data that the device's `.read()`
        function returns, using the Ophyd keys as CAspy internal
        keys.

        Args:
            cls: Ophyd class to use, in the notation
              `module.sub:Class`

            *oa: positional arguments to pass on to
              the Ophyd class constructor

            mode: Data acquisition mode, one of "subscribe" or "poll".
              "subscribe" is the default.

            **okw: keyword arguments to pass on to the
              Ophyd class
        '''

        cls_obj = self._get_class(cls)
        self._ovar = cls_obj(*oa, **ookw)

        self._auto_opcast = opcast

        if mode is None:
            # We don't support subscribe mode for Ophyd devices
            # that don't have a "value" type event to subscribe to.
            mode = 'subscribe' if "value" in self._ovar.event_types \
                else 'poll'

        if mode == 'subscribe':
            for et in ("value", "acq_done"):
                if et  in self._ovar.event_types:
                    self._ovar.subscribe(self._data_incoming, et)
                    logger.info(f'msg="Subscribing" sub_type={et} ophyd={self._ovar.name}')
                    break
            self._retr_data = self._retr_data_subscribe
            
        elif mode == 'poll':
            self._retr_data = self._retr_data_poll
            
        else:
            logger.error(f'msg="Unsupported mode" mode={mode}')
            raise RuntimeError(f'Bad mode "{mode}"')

        self._trigger_init = False
        self._trigger_readout = trigger
        self._stage_init = stage in ("once", )
        self._stage_readout = stage in ("always", "yes")

        self._disconn_reported = None
        self._data_lock = asyncio.Lock()

        self._data_cache = {}

        super().__init__()


    def _get_class(self, cspec):
        parts = cspec.split(':')

        if len(parts) != 2:
            raise RuntimeError(f'msg="Ophyd source needs a `<module>:<class>` spec"')
        
        logger.info(f'msg="Finding Ophyd device" '
                    f'class_name="{parts[1]}" '
                    f'module_name="{parts[0]}"')
        mod_obj = importlib.import_module(parts[0])
        cls_obj = getattr(mod_obj, parts[1])

        return cls_obj


    def _name2tag(self, name):
        # Ophyd names sometimes have ':' and '.' in them.
        # We need to strip those away.
        return ''.join([
            (c if c.isalnum() else '_') for c in name
        ])


    async def _maybe_prepare(self, proc, condition):
        if hasattr(self._ovar, proc) and condition:
            await asyncio.get_event_loop().\
                run_in_executor(None, getattr(self._ovar, proc))


    async def startup(self):
        await self._data_lock.acquire()
        await asyncio.get_event_loop().run_in_executor(
            None, self._ovar.wait_for_connection
        )
        await self._maybe_prepare("stage", self._stage_init)


    async def shutdown(self):
        await self._maybe_prepare("unstage", self._stage_init)
        await asyncio.get_event_loop().run_in_executor(
            None, self._ovar.disconnect
        )        


    async def _retr_data_poll(self):
        try:
            await self._maybe_prepare("stage", self._stage_readout)
            await self._maybe_prepare("trigger", self._trigger_readout)

            tree = await asyncio.get_event_loop().\
                run_in_executor(None, self._ovar.read)

            return {
                self._name2tag(k):d['value'] for k,d in tree.items()
            }

        finally:
            await self._maybe_prepare("unstage", self._stage_readout)            


    async def _retr_data_subscribe(self):

        # There's a bug on some versions of asyncio (?) which will prevent
        # the coroutine from waking up once the lock is released. Doing this
        # in a loop apparently works around this.
        while True:
            try:
                await asyncio.wait_for(self._data_lock.acquire(), timeout=0.01)
                break                
            except TimeoutError:
                continue
            
        if isinstance(self._data_cache, dict):
            return self._data_cache
        else:
            return await self._retr_data_poll()


    def _data_incoming(self, **kw):
        etype = kw['sub_type']
        
        if etype == 'value':
            val = kw['value']
            oldv = kw['old_value']
            ts = kw['timestamp']
            obj = kw['obj']

            if self._data_cache is None:
                raise RuntimeError(f'Looks like you\'re mixing "value" and '
                                   f'"acq_done" events; don\'t do that.')

            if self._auto_opcast:
                v = opcast(val, type_sequence=(int, float, np.array, str))
            else:
                v = val
            self._data_cache[self._name2tag(obj.name)] = np.array(v)

            try: self._data_lock.release()
            except RuntimeError: pass
                
        elif etype == 'acq_done':
            # Need to retrieve data...?
            # We completely invalidate the data cache, and let _retr_data_subscribe()
            # retrieve the data by issuing one .read() opeartion.
            self._data_cache = None
            if self._data_lock.locked():
                self._data_lock.release()

        else:
            logger.error(f'msg="Unexpected event" type="{etype}"')


    async def __call__(self, data=None, context=None):
        try:
            d = await self._retr_data()
            
            if self._disconn_reported == True:
                logger.info(f'msg="Ophyd device available again" '
                            f'name="{self._ovar.name}"')
                self._disconn_reported = False

            return d

        except (ophyd_errors.DisconnectedError,
                caproto.CaprotoTimeoutError):
            if self._disconn_reported in (None, False):
                logger.warning(f'msg="Ophyd device not connected" '
                               f'name="{self._ovar.name}"')
                self._disconn_reported = True
            return {}
        
        except Exception as e:
            traceback.print_exc()
            logger.error(f'msg="Error retrieving Ophyd data" reason="{e}"')
            return None        
