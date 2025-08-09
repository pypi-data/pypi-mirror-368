import asyncio, contextlib, pprint, parse, logging

from camagick.processor import ProcessorBase, SourceBase
from camagick.probe import opcast
from camagick.ioc import IocServer, InstaInputPVDB

from caproto.server import server as ca_server

import numpy as np

logger = logging.getLogger(__name__)

class PvMapper:
    pass

class Processor(SourceBase):

    def __init__(self,
                 prefix: str = '',
                 hang: bool = True,
                 suppress: str = None,
                 **pvspec):
        '''
        Initializes an IOC-source processor.

        This one spans a number of PVs for external users / components to write
        data into.

        Args:
        
            prefix: the IOC prefix, will be prepended (verbatim, no trailing ":")
              to every PV.

            hang: if set to any of `True`, `1`, `"yes"`, `"any"` the processor will
              not pass on data until new data has explicitly been written to any of
              the variables. If set to `"no"`, `0`, `False`, the Processor will pass
              on data every time it is asked.

            suppress: One of "initial", "same", or `None` (the default). If set
              to "initial", the initial PV value -- one that wasn't explicitly set
              externally after startup -- won't be propagated, and the IOC will
              instead wait forever until at least one value is explicitly written.
              "same" will suppress propagation values that are the same as the value
              the PV already holds.
        
            **pvspec: mapping the data label (keys) to PVs (sans prefix) and optionally
              starting values, in the format `'label' -> 'PV:string(val)'`, or
              `{ 'label': 'PV:string' }`.
        '''

        # Extract the PV labels, names and initial values. If there's no initial value,
        # we use a float (0.0). This is a { label: (pvname, value) } map.
        self._pv_value_map = self._parse_pv_initial(pvspec)
        self._suppress = suppress.split(',') if suppress is not None else []

        # This is how we map things locally: full-pv <-> short name
        self._pv_map = {
            f'{prefix}{v[0]}':k \
            for k,v in zip(pvspec.keys(),self._pv_value_map.values())
        }
        self._pv_unmap = {}
        for k,v in self._pv_map.items():
            if v in self._pv_unmap:
                raise RuntimeError(f'Double mapping: {k} <-> {v}')
            self._pv_unmap[v] = k

        #logger.debug(f'map: {self._pv_map}')
        #logger.debug(f'unmap: {self._pv_unmap}')

        pvmap = { f'{prefix}{v[0]}':v[1] for k,v in self._pv_value_map.items() }
        self.ioc = InstaInputPVDB(pv_map=pvmap,
                                  hang=self._check_true(hang),
                                  suppress_initial=('initial' in self._suppress),
                                  suppress_same=('same' in self._suppress),
                                  verify=self._verify_pv_value)
        self.ioc_server = IocServer(self.ioc)


    async def _verify_pv_value(self, pvname, value):
        return await self.verify(self._pv_map[pvname], value)


    async def verify(self, tag, value):
        '''
        Called for every incoming value.

        If this raises an exception, the value is not propagated
        through the CA internals. (Typically `caproto.CaprotoValueError`?)
        If a modified value is returned, the modified value is
        propagated instead.
        '''        
        pass


    def _check_true(self, hang):
        if hang in (1, True):
            return True
        elif isinstance(hang, str):
            return hang.lower() in ("yes", "true", "any")


    def _parse_pv_initial(self, label_spec_dict):
        ret = {}
        for label, spec_param in label_spec_dict.items():
            spec = str(spec_param)
            result = parse.parse('{name}({value})', spec)
            if result is not None:
                ret[label] = (result['name'], opcast(result['value']))
            else:
                ret[label] = (spec, np.nan)
        return ret

    
    async def startup(self):
        await self.ioc_server.startup()


    async def shutdown(self):
        await self.ioc_server.shutdown()

    
    async def __call__(self, data=None, context=None):
        await asyncio.gather(self.ioc.wait_for_input(), return_exceptions=False)
        my_data = {}
        for k,v in self.ioc._pvdb.items():
            if isinstance(v, ca_server.PvpropertyString):
                my_data[self._pv_map[k]] = v.value[0]
            else:
                v = v.value \
                    if isinstance(v.value, str) or hasattr(v.value, "shape") \
                       else np.array(v.value)
                my_data[self._pv_map[k]] = v

        #if self._transparent and data is not None:
        #    my_data.update(data)

        return my_data 



async def test_run():
    p = Processor(prefix='Jinkies:', hang=False,
                  scan='Scan(3.14)', stan='Stan(34)')
    await p.startup()

    try:
        while True:
            data = await p()
            print(data)
            
    finally:
        await p.shutdown()
    

if __name__ == "__main__":
    asyncio.run(test_run())
