import asyncio, pytest, time
import tango.asyncio as tas

from tango import DevState, GreenMode
from tango.server import Device, command, attribute
from tango.databaseds.database import main as srv_main

import multiprocessing as mp

from camagick.source.tango import Processor as TangoSource
from camagick.sink.tango import Processor as TangoSink

class AsyncioDevice(Device):
    green_mode = GreenMode.Asyncio

    async def init_device(self):
        await super().init_device()
        self.set_state(DevState.ON)

    @attribute
    async def detail(self):
        return 3.14


@pytest.fixture(scope='function')
def tsrv():
    host = '127.0.0.1'
    port = '10000'
    p = mp.Process(target=srv_main, args=[(
        '2', '-host', host,'-port', port,
    )])
    p.daemon = True
    p.start()
    time.sleep(1.0)
    yield (host, port)
    p.terminate()


def dev_main(inst, host, port):
    from os import environ
    environ['TANGO_HOST'] = f'{host}:{port}'
    AsyncioDevice.run_server(inst)


@pytest.fixture(scope='function')
async def tdev(tsrv):
    inst = '1' #devices/caspytest/1'
    args = [[f'{inst}'], *tsrv]
    print('Tango server running @', tsrv, args)
    p = mp.Process(target=dev_main, args=args)
    p.daemon = True
    p.start()
    yield inst, *tsrv
    p.terminate()
    

async def _test_tdev(tdev):
    print(f'Connecting to Tango test device {tdev}')

    import os
    old_tango_host = os.environ.get('TANGO_HOST', None)

    try:

        os.environ['TANGO_HOST'] = f'{tdev[1]}:{tdev[2]}'
        print('Tango host env-var:', os.environ['TANGO_HOST'])        
        
        src = TangoSource(dev=f'AsyncioDevice/{tdev[0]}', detail='detail')
        await src.startup()
        data = await src()
        print(f'Received: {data}')
        #inst = '3'
        #AsyncioDevice.run_server(inst) #, '-host', '127.0.0.1', '-port', '10000')

        await asyncio.sleep(10.0)
        await src.teardown()

    finally:
        if old_tango_host is not None:
            os.environ['TANGO_HOST'] = old_tango_host
