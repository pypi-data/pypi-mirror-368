from caproto.asyncio.server import Context as ServerContext
from caproto.server import PVGroup, pvproperty, PVSpec
from caproto import ChannelData
import caproto

from contextlib import suppress

import asyncio, logging

logger = logging.getLogger(__name__)


class DynamicMergeDict:
    ## El-Cheapo dictionary class that _dynamically_ returns items
    ## from a number of sub-dictionaries. Need this to manage the .pvdb
    ## of all common CAspy IOCs.
    
    def __init__(self):
        self.subs = []
        
    def add_sub(self, sub):
        self.subs.append(sub)

    def __getitem__(self, key):
        for s in self.subs:
            try:
                return s[key]
            except KeyError:
                pass
        raise KeyError(key)


    def __setitem__(self, key, val):
        raise RuntimeError('Nope.')


    def __repr__(self):
        return ' '.join([str(s) for s in self.subs])


    def __len__(self):
        return sum([len(s) for s in self.subs])


    def __contains__(self, key):
        for s in self.subs:
            if key in s:
                return True
        return False


class IocServer(object):
    ## Singleton IOC server class.
    ##
    ## Only this class ever spans an IOC. All other "IOCs" are actually
    ## just PV databases that eventually end up served by this one.
    ##
    ## Usage:  IocServer(pv_class)
    ##
    ## ...where pv_class has a .pvdb property that actually exposes PVs.
    
    def __new__(cls, *args, **kw):
        if not hasattr(cls, 'instance'):
            cls.instance = super(IocServer, cls).__new__(cls)
            cls.instance.__init_once__(*args, **kw)
            
        cls.instance.__init_always__(*args, **kw)
        return cls.instance

    
    def __init_once__(self, ioc):
        self.ioc_list = []
        self.refcnt = 0
        self.dyn = DynamicMergeDict()

    def __init_always__(self, ioc):
        self.ioc_list.append(ioc)
        self.dyn.add_sub(ioc.pvdb)


    @property
    def pvdb(self):
        return self.dyn


    async def startup(self):
        if self.refcnt == 0:
            self._name = f'IocServer'
            self.ctx = ServerContext(self.pvdb)
            self.task = asyncio.create_task(self.ctx.run(), name=self._name)
        self.refcnt += 1


    async def shutdown(self):
        if self.refcnt > 0:
            self.refcnt -= 1
        else:
            self.task.cancel()
            with suppress(asyncio.CancelledError):
                await self.task


class InstaOutputPVDB:
    ## Simple Output IOC class
    ##
    ##   .publish(name, data)
    ##
    ## ...makes sure that `data` ends up in the local EPICS
    ## network as a pv named `name`. PV is created on first
    ## .publish().
    
    def __init__(self):
        self.pv_dict = {}


    def _shape_size(self, s):
        if len(s)>1:
            return s[0] * self._shape_size(s[1:])
        elif len(s)==1:
            return s[0]
        else:
            return 1


    async def _publish_awaitable(self, name, val):
        # Returns an awaitable which sets val -> pv[name],
        # or creates pv[name] with a default value if it doesn't exist.

        print('writing PV:', name, '->', val)
        
        if name in self.pv_dict:
            if isinstance(val, str):
                return await self.pv_dict[name].write(val)
            else:
                return await self.pv_dict[name].write(val[()])

        else:
            #print('publish:', name, val)
            l = self._shape_size(val.shape)
            flat = val.flatten()
            dtype = type(flat[0].item())
            logger.info(f'msg="Creating PV" pvname="{name}" tag="{name}" length={l} '
                        f'shape={val.shape} dtype={dtype}')

            additional = dict(
                max_length=l
            )
            
            if dtype == str:
                additional.update(dict( max_length=40, ))
                dtype=caproto.ChannelType.STRING

            self.pv_dict[name] = PVSpec(name=name,
                                        value=flat,
                                        dtype=dtype,
                                        **additional).create(None)


    async def publish(self, name, val):
        await self._publish_awaitable(name, val)


    async def publish_many(self, set_dict, raise_errors=False):
        '''
        Publishes `data` as PV `name`.

        If the PV doesn't yet exist in `.pvdb`, a new PV is
        created.
        '''

        result = await asyncio.gather(*[
            self._publish_awaitable(name,val) for name,val in set_dict.items()
        ], return_exceptions=False)

        for r in result:
            if isinstance(r, Exception):
                logger.error(r)
                if raise_errors:
                    raise r
        

    
    @property
    def pvdb(self):
        return self.pv_dict



class InstaInputPVDB:
    '''
    Insta-PVDB specifically for the purpose of ingesting data.

    Exposes a .pvdb (to be used with whatever ServerContext contstruction),
    and exposes a .wait_for_input(), which releases once there's input
    available.
    '''

    def __init__(self, pv_map, hang=True,
                 suppress_initial=False,
                 suppress_same=False,
                 verify=None):
        '''
        Args:
            pv_map: map name -> value with the PVs to serve.

            suppress_initial: if set to `True`, the readout lock won't
              be lifted for the initial value -- only on explicit setting
              of the value.

            suppress_same: if set to `True`, the readout lock won't be
              lifted if the value written to PV is the same as the one
              the PV already has.
        
            verify: if not `None`, it's expected to be an async
              callable with the signature `verify(pvname, value)`
              called for incoming values, before processing them.
              If the value needs to be modified, the modified value
              needs to be returned. If `CaprotoValueError` is raised,
             then the value will not be updated and the CA protocol
             will propagate an error event instead.              
        '''

        self._hang = hang
        self._suppress_same = suppress_same
        self._suppress_initial = suppress_initial
        self._run_startup = True
        
        self._pvdb = {}
        self._pv_map = pv_map
        self._verify = verify

        self._input_lock = asyncio.Lock()

        for name,value in pv_map.items():

            if isinstance(value, str):
                self._pvdb[name] = PVSpec(
                    value=value,
                    name=name,
                    put=self._on_input,
                    dtype=caproto.ChannelType.STRING,
                    max_length=40,
                ).create(group=None)

            else:
                self._pvdb[name] = PVSpec(
                    value=value,
                    name=name,
                    put=self._on_input,
                ).create(group=None)

        for k in self._pvdb:
            logger.info(f'msg="Serving input PV" name={k}')


    async def _on_startup(self):
        # This should be done only once, on startup (but cannot be done
        # in __init__ since we need to await a lock acquisition.
        self._run_startup = False
        if (self._suppress_initial == True) and (not self._input_lock.locked()):
            print('initial suppress:', [k for k in self._pvdb.keys()])
            await self._input_lock.acquire()


    async def _on_input(self, pvinst, val):
        if self._verify is not None:
            v = await self._verify(pvinst.name, val)
        if self._hang and self._input_lock.locked():
            if not (self._suppress_same and val == pvinst.value):
                print('releasing:', pvinst.name, val, pvinst.value)
                self._input_lock.release()
            else:
                logger.info(f'msg="Suppressing unchanged PV value" '
                            f'pv="{pvinst.name}" '
                            f'value={val}')
                raise ValueError(f'value unchanged ({val})')
        if (self._verify is not None) and (v is not None):
            return v


    async def wait_for_input(self):
        # If we're already waiting for new input, the lock cannot be acquired --
        # so we need to wait.
        # Once we're free, we re-acquire the lock (to avoid repeated new_input()
        # until the next time the input condition is met).

        if (self._run_startup == True):
            await self._on_startup()

        if self._hang:
            print('waiting for:', [k for k in self._pvdb])
            await self._input_lock.acquire()


    @property
    def pvdb(self):
        return self._pvdb    
