#!/usr/bin/python3

import asyncio, time, logging

from caproto.sync import client as ca_client
from caproto.asyncio.client import Context
from caproto import CaprotoTimeoutError
import numpy as np

import copy

from xarray import DataArray
from functools import partial
from contextlib import suppress

logger = logging.getLogger(__name__)

class PvRetry(RuntimeError):
    '''
    Raised by GuidedPvReader when the PVs are not yet ready / guide does
    not yet signal readiness for signal readout.
    '''
    def __init__(self, *p, **kw):
        super().__init__(*p, **kw)


class DataInbox:
    ## Base class to manage various types of readout strategies.
    ## All have in common that data is (possibly) kept in a cache
    ## until a specific readout condition is met.
    ##
    ## Waiting is implemented by means of an async lock.
    
    def __init__(self, dwell=0.2):
        # This is where we cache the data.
        # We use full PV names as keys.
        # The payload ("data hold") is:
        # {
        #    'tag': short,
        #    'data': [list of datapoints],
        #    'ts': [timestamps]
        # }
        self._incoming_data = {}
        self._dwell_time = dwell


    def _release_lock(self):
        with suppress(RuntimeError):
            self._readout_lock.release()


    async def _readout_lock_acquire(self, timeout=None):
        if timeout is None:
            await self._readout_lock.acquire()
        else:
            await asyncio.wait_for(self._readout_lock.acquire(), timeout)


    def _have_complete_set(self):
        ## Checkes whether a complete data set (as expected) is available.
        have = [ k for k in self._incoming_data.keys() ]
        for x in self._expected:
            if x not in have:
                return False # don't have a full set, NO READOUT
        return True


    def _trim_backlog(self, num_max=1):
        ## Removes all but `num_max` data entries from every PV's backlog.
        ## This MUST BE CALLED if they don't reset the backlog altogether.
        for pvname,hold in self._incoming_data.items():
            if len(hold['data']) > num_max:
                del hold['data'][:num_max]
                del hold['ts'][:num_max]


    def _reset_backlog(self):
        self._incoming_data = {}


    async def create(self, expected):
        '''
        Called when within the designated asyncio loop.

        Expected to perform initialization steps that can only be
        performed from within the loop.

        Args:
            expected: List of expected full PV set. Used for various decision-making
              procedures (see also ._have_complete_set()).
        '''
        self._expected = expected
        self._readout_lock = asyncio.Lock()


    def ingest(self, pvname, tag, response):
        '''
        Called when incoming data is arriving.

        Args:
            pvname: full PV name
            tag: short name (not used? may be "none"?)
            response: CAproto response object; contains `.data`
        '''
        hold = self._incoming_data.setdefault(
            pvname,
            {
                'tag': tag,
                'data': [],
                'ts': []
            }
        )
        hold['data'].append(response)
        hold['ts'].append(time.time())


    async def readout(self, timeout=None):
        '''
        Returns data, if this is the case according to readout policy.

        Might block until readout is due.
        '''
        if self._dwell_time > 0.0:
            await asyncio.sleep(self._dwell_time)

        # return only the last item of each key (not the whole incoming stack)
        return {
            k:{'data': v['data'][-1], 'ts': v['ts'][-1]} \
            for k,v in self._incoming_data.items()
        }


class ContinuousDataInbox(DataInbox):
    '''
    Continuous and uncoditional EPICS readout.
    No waiting for (new) data, no resetting of the readout
    buffer.
    '''
    def ingest(self, pvname, tag, response):
        super().ingest(pvname, tag, response)
        self._trim_backlog()
    

class LockingDataInbox(DataInbox):
    ## Base class that locks the ._readout_lock generally (at the
    ## beginning, and usually after readout), and only unlocks it
    ## when a new dataset is available.
    ## Essentially everything except ContinuousDataInbox depends
    ## on this.

    def can_readout(self):
        ## This is checked on every ingest. Default behavior for
        ## most modes is "yes, we can read out". But some specific
        ## modes -- i.e. "thorough" and possibly "guided" -- will
        ## overwrite this to implement a more sophisticated method.
        return True

    async def create(self, expected):
        await super().create(expected)
        await self._readout_lock_acquire()

    def ingest(self, pvname, tag, response):
        super().ingest(pvname, tag, response)
        self._trim_backlog()
        if self.can_readout():
            self._release_lock()

    async def readout(self, timeout=None):
        await self._readout_lock_acquire(timeout)
        d = await super().readout()
        return d


class GuidedDataInbox(LockingDataInbox):

    def __init__(self, guide_dict, **kwargs):
        super().__init__(**kwargs)

        if guide_dict is None:
            guide_dict = {}
        
        # This is a dictionary guide-pv <-> test lambda
        self.guides = {}
        self.guides.update({
            k:v if hasattr(v, "__call__") else lambda k,x: x == v \
            for k,v in guide_dict.items()
        })

        # map EPICS name -> current True/False  evaluation of the guide signal.
        # Note that this is _not_ the guide trigger evaluation, i.e. the condition
        # of whether the waiting for this guide is finished and we're ready to
        # return data! For the latter to be fulfilled, the corresponding
        # guide_eval needs to be changing from 'False' to 'True'!
        self.guide_evals = { k:None for k in self.guides }


    async def create(self, expected):
        await super().create(expected)
        self.guide_trigger = {
            k:False for k in self.guides.keys()
        }


    def _guide_changed(self, pv_name, response):
        '''
        Called when a guide value changes. Checks if all guide conditions
        are met, and possibly calls the incoming hooks.
        '''

        d = response.data if len(response.data) > 1 else response.data[0]
        eval_result = self.guides[pv_name](pv_name,d)

        logger.info(f'msg="Guide update" pv={pv_name} value="{d}" type={type(d)}')

        if eval_result:
            if not self.guide_evals[pv_name]:
                # on eval switch False -> True: trigger!
                self.guide_trigger[pv_name] = True
        else:
            # eval False always kills the trigger
            self.guide_trigger[pv_name] = False
            
        self.guide_evals[pv_name] = eval_result

        #print(eval_result, self.guide_evals, self.guide_trigger, self.guides[pv_name](pv_name,d))



    def can_readout(self):

        # check whether we can do a data readout (all triggers must be True)
        guides_ok = all(self.guide_trigger.values())

        if not guides_ok:
            return

        return True


    def _invalidate_guide(self):
        for k in self.guide_trigger:
            self.guide_trigger[k] = False


    def ingest(self, pvname, tag, response):
        if (pvname in self.guides):
            #logger.info(f'msg="Guide changed" name={pv_name} value={d} '
            #            f'condition_ok={eval_result} '
            #            f'activated_ok={self.guide_evals[pv_name]} '
            #            f'all_ok={guides_ok}')
            self._guide_changed(pvname, response)
        return super().ingest(pvname, tag, response)


    async def readout(self, timeout=None):
        data = await super().readout()
        self._invalidate_guide()
        not_guide = lambda x: x[0] not in self.guides
        return { k:v for k,v in filter(not_guide, data.items()) }


class SloppyDataInbox(LockingDataInbox):
    '''
    Unlocks the readout as soon as _any_ data is available.
    Don't reset the readout (meaning that subsequent ingest
    operations will eventually return a full set of data,
    but possibly from different points in time).
    '''
    pass

        
class HastyDataInbox(SloppyDataInbox):
    '''
    Same as SloppyDataInbox (i.e. returns data on _any_ ingest),
    but reset the backlog on retrieve. This means that there
    will almost never be a full dataset available (unless 'dwell'
    is sufficiently large).
    '''
    async def readout(self, timeout=None):
        d = await super().readout(timeout)
        self._reset_backlog()
        return d


class ThoroughDataInbox(SloppyDataInbox):
    '''
    Returns the data only when a full dataset is available.
    Resets the backlog afterwards, so that a _new_ full dataset
    is required for new readout.
    '''

    def can_readout(self):
        return self._have_complete_set()


class ClusteredDataInbox(DataInbox):
    # See also: https://web.stanford.edu/class/cs345a/slides/12-clustering.pdf
    pass

    

class AsyncReader:
    '''
    Observes a "guide" variable to determine when a specific EPICS PV signal is
    available, then collects the PV signal (which can come in a list of other PVs).    

    To get as efficient as possible, this implementation actually
    uses subscriptions to the guide variables, and reacts on
    those. Calling .value() will wait asynchronously for the guide
    conditions to be fulflled, and this will be fairly efficient.

    But the most efficient way will be to subscribe a data
    processing callback using .subscribe(), which will be called
    only when all guide conditions are fulfilled and all data
    is available.
    '''

    def __init__(self,
                 *pvs: list,
                 guide_dict: dict = None,
                 mode: str = '',                 
                 auto_xarray: bool = True,
                 dwell: float = None):
        '''
        Initialises the reader.

        Args:
        
            pvs: The PVs to read out. (If not specified here, they can
              be specified later -- FIXME: really?)
              All PVs to be monitored are being subscribed to, and the newest
              version of incoming data is stored without backlog (!), until
              the guide conditions are all met.
        
            guide_dict: A dicitonary of guide variable(s) as keys, and a
              corresponding value to use, OR a callable of the signature
              `proc(key, value)`.
              The "guide condition" is "activated" for each individual guide
              when the callable returns `True` for the first time; the "guide
              condition" is "met" when _all_ guides have been activated.
                      
              When the guide condition is met, the current values of the PVs
              specified in `pvs` are returned as readout, and a new readout
              is only possible after a new reactivation. Note that for a new
              reactivation, a *de*activation of the individuals is necessary
              first, and that a *de*activation is *not* done automatically.
              Rather, it is expected that the guides deactivate themselves
              by taking on a value that doesn't meet the activation condition.

              Thus, guides are required to "blink" at least once for every
              data readout.
        
            mode: Readout mode, one of "hasty", "sloppy", "continuous",
              "thorough", "guided" or "clustered". See documentation of
              `camagick.source.epics` for a detailed explantion on the
              readout mode.

            guide_probe: A single probe object to signalize the guide condition.

            dwell: Time (in seconds) to wait after guide condition is met
              until data is collected. ACHTUNG: the wait is performed only
              for `.wait_for_data()`, not when using data callbacks!
        '''

        self.pvs = [v for v in pvs]
        
        for v in (guide_dict if guide_dict is not None else {}):
            if v not in pvs:
                self.pvs.append(v)
                continue
            logger.warning(f'msg="PV explicitly requested as data _and_ guide will '
                           f'not be returned as data" name={v}')
        
        # DEACTIVATED (old legacy code, not sure it's useful anymore...)
        #
        #    auto_xarray: If set to `True`, data is transformed to `xarray` data
        #      set rather than `numpy` arrays, and some implicit conversions and
        #      enhancements are triggered. These are... (FIXME: explain!)        
        self.auto_xarray = False
        #if auto_xarray:
        #    for k in self.pvs:
        #        if k.endswith("_SIGNAL"):
        #            kbase = k.replace('_SIGNAL', '')
        #            self.pvs.append(f'{kbase}_OFFSET')
        #            self.pvs.append(f'{kbase}_DELTA')


        if mode is None or len(mode) == 0:
            if guide_dict is None or len(guide_dict)==0:
                mode = 'sloppy'
            else:
                mode = 'guided'

            if dwell is None:
                dwell = 0.1
    
            logger.info(f'msg="EPICS readout mode autodetection" '
                        f'mode="{mode}" dwell={dwell}')
        else:
            logger.info(f'msg="Explicit EPICS readout mode" mode="{mode}"')

        # inbox needs to be initialized in a running asyncio loop.
        self.inbox = {
            'hasty': partial(HastyDataInbox, dwell=dwell),
            'sloppy': partial(SloppyDataInbox, dwell=dwell),
            'continuous': partial(ContinuousDataInbox, dwell=dwell),
            'thorough': partial(ThoroughDataInbox, dwell=dwell),
            'guided': partial(GuidedDataInbox, guide_dict=guide_dict, dwell=dwell),
            'clustered': partial(ClusteredDataInbox, dwell=0.0)
        }[mode]()

        self.ctx = None #ctx

        self.data_pvs = None
        self.incoming_hooks = []

        self._ref_cnt = 0


    async def __aenter__(self):
        if self._ref_cnt == 0:
            await self.connect()
        self._ref_cnt += 1
        return self


    async def __aexit__(self, *a, **kw):
        if self._ref_cnt > 0:
            self._ref_cnt -= 1
        if self._ref_cnt == 0:
            await self.disconnect()


    async def connect(self, ctx=None):
        
        if ctx is not None:
            self.ctx = ctx
            
        if self.ctx is None:
            logger.info(f'msg="Creating CA client context"')
            self.ctx = Context()
            self.own_ctx = True
        else:
            logger.info(f'msg="Reusing CA client context" ctx="{self.ctx}"')

        # map PV name -> Context PV, for all non-guide variables
        self.data_pvs = await self.ctx.get_pvs(*[v for v in self.pvs])

        await self.inbox.create(expected = [ d.name for d in self.data_pvs])
            
        #  map EPICS name -> Subscription obj, for all guides
        self.data_subscriptions = {}

        for d in self.data_pvs: # + self.guide_pvs:
            logger.info(f'Subscribing to data: {d.name}')
            self.data_subscriptions[d.name] = d.subscribe()
            self.data_subscriptions[d.name].add_callback(self._data_changed)
        

        # map EPICS name -> trigger-condition-fulfilled, for all guides.
        # When all of these are True, that's when we need to read
        # all the non-guide data.
        # Each of these becomes True when the guide changes value _to_
        # whatever was specified. It switches to False again when a data
        # readout is performed, or when it swithces value away _from_
        # whatever was specified.
        #
        # Note that this is subtly different from self.guide_evals!
        # While guide_evals is a True/False value per guide, representing
        # the current condition evaluation, the guide_trigger truth value
        # also indicates the *changing* to the True value.
        #
        # Also important to note: keeping this accurate for _all_ guides
        # at once is difficult when more than one guide is involved (values
        # will change with a slight delay). Hence the policy: once a guide
        # is considered triggered, it _stays_ triggered for as long as
        # its value doesn't chance, or data isn't read.

        logger.info(f"New CA context state: {self.ctx}")


    async def disconnect(self):
        if hasattr(self, "own_ctx") and self.own_ctx == True:
            await self.ctx.disconnect()
        

    def extract_data(self, response, pvName=None, others=None):
        '''
        Extracts "useful" data out of a response telegram.
        '''

        if response is None:
            return None

        if others is None:
            others = {}

        # Channel types can be: CHAR, DOUBLE, FLOAT, STRING, ENUM, LONG, INT.
        # The intention is to get an automatic useful native Python data type,
        # scalar or array. This means different things for different data
        # types.
        # In addition, we implement some heuristics to decorate waveforms
        # (== arrays) if our obscure array markers are present (shape, dimensions,
        # axis scaling -- to be documented ;-) )
        
        if response.data_type in (ca_client.ChannelType.STRING,):
            return response.data[0].decode('utf-8')
        
        elif response.data_type in (ca_client.ChannelType.DOUBLE,
                                    ca_client.ChannelType.FLOAT,
                                    ca_client.ChannelType.LONG,
                                    ca_client.ChannelType.INT,
                                    ca_client.ChannelType.ENUM):
            
            if len(response.data) == 1:
                return response.data[0]

            if not pvName or not pvName.endswith("_SIGNAL"):
                return response.data
            
            # If we have an array and it ends on _SIGNAL, we also try to
            # load _OFFSET and _DELTA for intrinsic scaling information
            o_name = pvName.replace("_SIGNAL", "_OFFSET")
            d_name = pvName.replace("_SIGNAL", "_DELTA")

            if o_name in others:
                offs = self.extract_data(others.get(o_name, 0))
            else:
                offs = 0

            if d_name in others:
                dlta = self.extract_data(others.get(d_name, 1))
            else:
                dlta = 1

            try:
                axis = offs+np.array(range(len(response.data)))*dlta
            except TypeError as e:
                # This happens when not all the data (e.g. `dlta` or `offs`
                # has arrived yet.
                axis = np.array([np.nan] * len(response.data))

            if self.auto_xarray:
                return DataArray(data=response.data, dims=["x"], coords=[axis])
            else:
                return response.data

        elif response.data_type in (ca_client.ChannelType.CHAR,):
            # This is a string -- return as such (ACHTUNG, this will break
            # "everything is a numpy array" data philosophy -- but we _want_
            # this. There's no other way to discern a uint8 from a string
            # later on.
            p = response.data
            s = bytes(p).decode('utf-8')
            return s

        elif response.data_type in (ca_client.ChannelType.STRING,):
            # This is a string -- return as such (ACHTUNG, this will break
            # "everything is a numpy array" data philosophy -- but we _want_
            # this. There's no other way to discern a uint8 from a string
            # later on.
            #print('have', repsonse.data)
            return response.data
        

        # else: how to handle ENUM / CHAR?
            
        else:
            logger.warning ("Unhandled data type: %r" % (response.data_type,))
            return response.data[0]


    def subscribe_incoming(self, proc):
        '''
        Registers a hook for processing incoming data.
        
        The hook will receive a dictionary with full PV
        name(s) as keys, and data as values, when guide condition is met.
        '''
        self.incoming_hooks.append(proc)


    def _data_changed(self, sub, response):
        '''
        Called when new data arrives.
        '''
        self.inbox.ingest(sub.pv.name, None, response)

    
    async def _get_incoming(self):
        '''
        Returns the currently incoming data (from subscriptions).
        We're using this instead of directly reading out the `._incoming_data`
        dictionary because, optinally, we're doing some mangling
        in `.extract_data()` that may or may not interfere with
        the data keys.
        '''

        # need to work on a copy here because _incoming_data might change
        # while we're waiting for new incoming data.
        tmp = await self.inbox.readout()

        return {
            k:self.extract_data(v['data'], k, others=tmp) \
            for k,v in tmp.items() \
            if (v is not None)
        }


    async def wait_for_incoming(self):
        '''
        Waits for incoming data. Returns only once per read-cycle
        (i.e. "marks" itself as called, so that repeated calls to
        this function sleep until new data is actually available,
        according to the ._readout_mode strategy).
        '''

        d = await self._get_incoming()
        return d


# Legacy name
GuidedAsyncReader = AsyncReader
