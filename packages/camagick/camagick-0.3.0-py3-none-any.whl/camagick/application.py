#!/usr/bin/python3

import argparse, os, asyncio, importlib

#from camagick.stash import ZarrStash
#from camagick.helpers import FpsCounter
#from camagick.processor import ProcessorBase

#class CAMagickApplication(ProcessorBase):
#    '''
#    Base class from which all CAMagick applications are derived.
#    Implements access to the data stash and the seed/crop history.
#    (This is a bit of overlap with the Processor base class -- needs
#    refactoring.)
#    '''
#
#    pass

    #def __init__(self, args=None, env=None, name=None,
    #             description="CAMagick Application", init=True):
    #    
    #    self._args = args if args is not None else sys.argv
    #    self._env = env if env is not None else os.environ.copy()
    #    self.applicationName = name or os.path.basename(self._args[0])
    #    
    #    self.argparser = self._create_base_argparser(description)

        
    #async def init_base(self, args):
    #    self.stash = ZarrStash(args.stash, lockKey=args.lock)
    #    self.fps = FpsCounter(100)


    #def _create_base_argparser(self, description):
    #    # Create argparser, add basic functionality arguments
    #    # (mostly just data exchange)
    #    #foo = argparse.ArgumentParser()
    #    foo = argparse.ArgumentParser(prog=self.applicationName,
    #                                  description=description,
    #                                  add_help=False)        
    #    foo.add_argument('--stash', action='store',
    #                     help='File path for the data stash')
    #    foo.add_argument('--lock', action='store',
    #                     help='Lock key to use for synchronising access to data')
    #
    #    return foo
    #
    #
    #def run(self):
    #    asyncio.run(self.async_run())
