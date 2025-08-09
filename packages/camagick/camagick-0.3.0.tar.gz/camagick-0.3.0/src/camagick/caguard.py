#!/usr/bin/python3

import os, sys, asyncio, time, logging
from camagick.probe import *

logger = logging.getLogger(__name__)

class Application:

    def __init__(self, args=None, env=None):
        self._args = args or sys.argv.copy()
        self._env  = env or os.environ.copy()

    async def startup(self):
        self._probe = make_probe(self._args[1:])
        logger.debug(f'input={self._args[1:]} probe={self._probe}')


    async def shutdown(self):
        pass
        

    async def run(self, period=0.1):
        if not hasattr(self, "_probe"):
            await self.startup()
            shut_me_down = True
        else:
            shut_me_down = False
            
        try:
            while self._probe():
                await asyncio.sleep(1)
            logger.debug(f'msg="Probe negative" expr={self._probe}')
        except Exception as e:
            from traceback import format_exc
            logger.error(f'msg="Probe error, traceback follows" detail={e}')
            logger.error(traceback.format_exc())
        finally:
            if shut_me_down:
                self.shutdown()


def main(args=None, env=None):
    app = Application(args or sys.argv, env or os.environ)
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
