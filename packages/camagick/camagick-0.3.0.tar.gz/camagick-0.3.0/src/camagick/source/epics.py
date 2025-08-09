import caproto.asyncio.client as ca

import xarray, sys, argparse, logging, time, math, os, asyncio, traceback, pprint

from camagick.helpers import FpsCounter
from camagick.stash import ZarrStash
from camagick.reader import AsyncReader
from camagick.processor import ProcessorBase, SourceBase

from camagick.probe import opcast

logger = logging.getLogger(__name__)

class Processor(SourceBase):
    '''
    Reading from existing EPICS PVs

    The module retrieves data from EPICS process variables (PVs) that
    exists in your network. There are various tuning possibilities,
    including using other EPICS PVs as "guides" -- this means that the
    reading process will only be performed when the "guides" change
    to a certain value for the first time after having _not_ had that
    value.

    CLI Examples:
      Various readout scenarii, with data output to `--to-summary` for
      demonstration purposes:

      - Reding with auto-generated tag names:
        ```
        caspy --from-epics EXAMPLE:iffy --to-summary
        caspy --from-epics EXAMPLE:iffy EXAMPLE:jedda --to-summary
        ```

      - Reading multiple with explicitly named tags:
        ```
        caspy --from-epics my_scalar=EXAMPLE:iffy \\
                           my_array=EXAMPLE:jedda \\
              --to-summary
        ```

      - Reading when "guide-PV" blinks to 0, with an explicit dwell time:
        ```
        caspy --from-epics my_scalar=EXAMPLE:iffy \\
                           my_array=EXAMPLE:jedda \\
                           when=\\"EXAMPLE:mark==0\\" \\
                           dwell=0.2 \\
              --to-summary
        ```

    YAML Examples:
      Use these with `caspy -y ...`:

      ```
      chain:
      - from: "epics"
        params:
          my_scalar: "EXAMPLE:jedda"
          my_array: "EXAMPLE:iffy"
          when: "EXAMPLE:mark==0"
          dwell: 0.2
      - to: summary
      ```
    '''

    def __init__(
            self,
            *simple_pvs,
            mode: str = '',
            prefix: str = '',
            guide: str = '',
            when: str = '',
            dwell: float = 0.1,
            **tagged_pvs
    ):
        '''
        Initialization the EPICS-PV source

        Subscribes to all variables in `pvname` and returns their contents
        every time all the conditions in `guide` are met for the first time.

        Args:
          *simple_pvs: PVs to return as data. Each must be a string,
            and each string will be used as its own tag. As such, it must
            _not_ have any Python non-symbol characters (like ":" or ".").
            To still make it possible to build EPICS PV names in a simple way,
            the actual PV address will be built as `f{prefix}{}`, where
            `prefix` is the corresponding parameter.

          mode: determines when the `.__call__()` operator returns the data.
            It all boils down to two decisions necessary when acquiring more
            than one single PV: (1) when is a composite dataset considered
            ready for processing, and (2) which data goes into a dataset?
            Supported modes:

              - hasty: deliver data when /any/ new data is available,
                discard data that has been retrieved. This means that
                there will almost never be a point when all required
                data keys are available at once, unless there's a
                sufficiently large `dwell` time.
                This is the default when `guide` is empty.

              - sloppy: similarly to hasty, but don't discard data that
                has been retrieved. This means that except for the very
                first few retrievals, there will always be a full data
                set, but some data items may be old and others may be
                fresh. This is the behavior that's closest to polling data.

              - continuous: like sloppy, but don't block waiting for new
                data. Just return whatever is in the queue, and don't clean
                up the queue. This is similarly to what continously polling
                all the variables would do, except that no polling is actually
                performed. (ACHTUNG: IOCs that depend on polling to actually
                trigger a hardware readout will *not* therfore work as
                expected!)

              - thorough: return data only when /all/ data items are acquired,
                and discard data afterwards. Every successful query will
                have a full set of fresh, new data. But if one PV isn't
                updated regularly, data flow will stall.

              - guided: return data when the guide condition is fulfilled
                for the first time after having /not/ been fulfilled.
                This is the default when `guide` is non-empty.

              - clustered: save a timestamp for each incoming data point,
                then cluster together data points with similar timestamps.
                Return data when a cluser is "complete", i.e. when incoming
                data points clearly don't belong to the same cluster
                anymore. `dwell` time is ignored here.

            If you have a traditional move-acquire-process loop at the
            base of your experimental orchestration, then the "clustered"
            is likely to give the best results. Alternatively, you can use
            "guided", possibly with a suitable `dwell`-time, if you have a
            clear and reliable marker of when your device's acquisition
            process is finished (note that EPICS, by its TCP/IP nature,
            is notoriously unreliable as to the order and timing of packets,
            so it will really just boil down to your `dwell`).

            "sloppy" and "thorough" will give good results for continous
            data, or as a visualisation aid (i.e. where there's no harm
            when data points from different acquisitions may accidentally
            interleave).

            "hasty" may be useful with a fitting `dwell` time, otherwise
            you'll end up sending data through your processing pipeline
            one item at a time. This /may/ me acceptable if your pipeline
            is not dependent (or sensitive) to having a full data set
            to work with.

          prefix: Prefix to prepend to each of the `simple_pvs` PV names.

          guide: key-value pairs of EPICS variables and values to change
            to for the reading condition to be met. (FIXME: will change soon)

          when: same as `guide`

          dwell: Time to wait after guide condition is met until data
            is collected. This is necessary because EPICS is inherently a
            /non-realtime/ TCP-IP based protocol. This means that even if
            the sending IOC does everything right and signals the readiness
            (via guides) only /after/ the data is available, there's still
            no guarantee that the data will arrive in time at the consuming
            EPICS client.

         **tagged_pvs: PVs specified as `tag=EPICS:pv:name`, accessing
           an EPICS PV named "EPICS:pv:name", and making it accessible
           to the `caspy` pipeline under the tag "tag"
        '''

        if when is not None and len(when)>0:
            guide = when

        if len(mode) == 0:
            mode = 'sloppy' if len(guide)==0 else 'guided'
        if guide in (None, '') and mode == 'guided':
            raise RuntimeError(f'msg="Guided mode requested for EPICS reader, but no guide specified"')

        if guide not in (None, '') and (mode not in ('guided', '', None)):
            raise RuntimeError(f'msg="Guides specified for wrong mode" mode="{mode}"')

        self.options = {
            'guides': self._make_guides(guide),
            'pvs': tagged_pvs,
            'dwell': dwell,
            'mode': mode
        }

        for simple in simple_pvs:
            if ':' in simple:
                pvtag = simple.replace(':', '_').replace('.', '_')
            else:
                pvtag = simple
            old_pv = self.options['pvs'].get(pvtag, None)
            new_pv = f'{prefix}{simple}'
            if old_pv is not None:
                raise RuntimeError(f'PV tag "{pvtag}" intended for "{new_pv}" '
                                   f'already present for PV "{old_pv}"')
            self.options['pvs'][pvtag] = new_pv


        self._pv2tag = {}
        for tag,pv in self.options['pvs'].items():
            old = self._pv2tag.get(pv, None)
            if old is not None:
                e = f'tag={tag} new_pv={pv} old_pv={old} msg="Double-tag error"'
                logger.error(e)
                raise RuntimeError(e)
            self._pv2tag[pv] = tag

        super().__init__()


    def _make_guides(self, gspec):
        if gspec is None or len(gspec)==0:
            return None
    
        parts = gspec.split('==')
        
        if len(parts) == 2:
            return { parts[0]: opcast(parts[1]) }


    async def startup(self):
        await self.init_epics(**self.options)


    async def shutdown(self):
        await self.epics_reader.disconnect()


    async def init_epics(self, guides=None, pvs=None, dwell=None, mode=''):
        self.epics_reader = AsyncReader(*[ v for k,v in pvs.items() ],
                                        guide_dict=guides,
                                        auto_xarray=False,
                                        dwell=dwell,
                                        mode=mode)

        await self.epics_reader.connect()


    async def __call__(self, data=None, context=None):
        if data is None:
            data = {}

        try:
            incoming = await self.epics_reader.wait_for_incoming()
            my_data = { self._pv2tag[k]:v for k,v in incoming.items() }

            #my_data.update(data)
            return my_data

        except Exception as e:
            traceback.print_exc()
            logging.error("Data retrieve failed: %r", e)
