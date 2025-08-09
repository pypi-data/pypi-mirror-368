#!/usr/bin/python3

import os, time, asyncio, glob, sys, logging, argparse, traceback

import camagick.source

#camagick_sources = {
#    k:getattr(camagick.source, k) for k in \
#    filter(lambda x: hasattr(getattr(camagick.source, x), 'populate_argparser'),
#           camagick.source.__dir__())
#}

from camagick.source.epics import Processor as EpicsSource
from camagick.sink.summary import Processor as SummarySink
from camagick.sink.hdfdata import Processor as Hdf5Sink
from camagick.sink.tiffseries import Processor as TiffSink
from camagick.sink.epics import Processor as EpicsSink
from camagick.pipe.slice import Processor as SlicePipe
from camagick.pipe.npstat1 import Processor as Stat1Pipe
from camagick.pipe.reshape import Processor as ReshapePipe
from camagick.pipe.fanout  import Processor as FanoutPipe
from camagick.pipe.chain  import Processor as ChainPipe

logger = logging.getLogger("camagick")

def find_subapps(module):
    names = [
        k for k in filter(
            lambda x: hasattr(
                getattr(module, x),
                "populate_argparser"
            ),
            module.__dir__())
    ]
    
    return { n:getattr(module, n) for n in names }


def make_argparser(name):
    ## Parses main application command options
    cap = argparse.ArgumentParser(prog=name)

    #sources_sub = cap.add_subparsers(dest="sources")

    for s_name,s_mod in find_subapps(camagick.source).items():
        logger.info(f'source={s_name} module={s_mod}')
        cap.add_argument(s_name, action='append')
        s_mod.populate_argparser(cap)

    return cap


class CAMagickApplication:
    
    def __init__(self, pipeline):
        self.pipeline = pipeline

        
    async def run(self):

        await self.pipeline.startup()
        
        try:
            in_data = None

            while True:
                out_data = await self.pipeline(in_data)
                if (out_data is not None) and len(out_data)>0:
                    logger.warning(f'msg="Residual data keys" keys="{out_data.keys()}"')


        except Exception as e:
            logger.error(e)
            logger.error('Good bye')

            traceback.print_exc(e)

        finally:
            await self.pipeline.shutdown()


def main(args=None, env=None):

    if args is None:
        args = sys.argv

    if env is None:
        env = os.environ.copy()

    logging.basicConfig()
    logger.setLevel("INFO")

    #ap = make_argparser("camagick")
    #ap.print_help()

    #opt = ap.parse_args(args[1:])

    chain = ChainPipe(
        EpicsSource(
            pvprefix="KE:threshold_1:",
            pvname=['image'],
            guide={ 'KE:acquire': 1, },
            context={
                'asize1': 'KE:threshold_1:width',
                'asize2': 'KE:threshold_2:height'
            }
        ),
        
        ReshapePipe(
            shape=(1, 512, 1028)
        ),
        
        FanoutPipe(
            #SummarySink(),
            #Hdf5Sink("/tmp/foo.h5#mega"),
            TiffSink("/tmp/Xcurrent-{tag}-{seq}-{asize1}x{asize2}-layer.tif"),
            ChainPipe(
                #SlicePipe(),
                FanoutPipe(
                    Stat1Pipe("max"),
                    Stat1Pipe("sum")
                ),
                
                # ACHTUNG, using this without a prefix will shadow any
                # EPICS PVs by the same name as the incoming data -- it only
                # works like this if the previous processing replaces all
                # the input keys. Otherwise you need to specify a different
                # prefix.
                EpicsSink()
            )
            
        )
    )

    app = CAMagickApplication(chain)

    asyncio.run(app.run())

if __name__ == "__main__":
    main()
