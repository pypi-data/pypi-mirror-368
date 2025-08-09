import pytest, asyncio, time, traceback
import multiprocessing as mp

from camagick.source.scratch import Processor as GenSource
from camagick.source.ioc import Processor as IocSource
from camagick.source.epics import Processor as EpicsSource

from camagick.sink.ioc import Processor as IocSink
from camagick.sink.epics import Processor as EpicsSink
from camagick.sink.summary import Processor as SummarySink

from camagick.flow.chain import Processor as ChainFlow
from camagick.flow.fanout import Processor as FanoutFlow

from camagick.pipe.pace import Processor as Pace
from camagick.pipe.only import Processor as Only
from camagick.pipe.exclude import Processor as Exclude

from camagick.executor import PipeExecutor

from camagick.reader import AsyncReader

import logging

def ioc_main(chain):
    logger = logging.getLogger("camagick")
    logging.basicConfig()    
    logger.setLevel(logging.DEBUG)
    asyncio.run(PipeExecutor(chain).run())


@pytest.fixture(scope='module')
def ioc():

    prefix = 'tee:'
    
    chain = ChainFlow(
        IocSource(prefix=prefix, mark="mark"),

        IocSource(prefix=prefix, counter1="counter1(0)", hang=False),

        GenSource("random", iffy=1, jiffy=100),
        Only(".*iffy"),
        IocSink(prefix=prefix),

        GenSource("zeros", "idle"),
        EpicsSink(idle="tee:mark"),

        IocSource(prefix=prefix, counter2="counter2(0)", hang=False),

        Pace(Hz=1.0),
        GenSource("ones", "busy"),
        EpicsSink(busy="tee:mark")
    )
    
    p = mp.Process(target=ioc_main, args=[chain], kwargs={})
    p.daemon = True
    p.start()

    #time.sleep(1.0)

    yield {
        'prefix': prefix,
        'process': p
    }

    print('Terminating IOC')
    p.terminate()
             

async def test_reader_continuous(ioc):
    pref = ioc['prefix']
    t0 = time.time()
    data = {}

    readout_vars = (
        f'{pref}iffy',
        f'{pref}mark'
    )

    async with AsyncReader(*readout_vars, mode="continuous", dwell=0.0) as reader:
        while (time.time()-t0) < 5.0:
            d = await reader.wait_for_incoming()
            if len(d) == 0:
                await asyncio.sleep(0.1)
                continue

            print('received:', d)
            if 'tee:iffy' in d:
                data.setdefault(d['tee:iffy'], 0)
                data[d['tee:iffy']] += 1
            print(data, len(d))

            # We're not sure how many items we receive on the first run,
            # but come the 2nd run, there should be one full set.
            if time.time()-t0 > 1.0:
                assert len(d) == 2

            await asyncio.sleep(0.2)

    ## We should have received 5 distinct random numbers,
    ## and each of them several times over.
    assert len(data) == 5
    for k,v in data.items():
        assert v > 1



async def test_reader_hasty(ioc):
    pref = ioc['prefix']
    t0 = time.time()
    data = {}

    received_sum = 0
    loop_sum = 0

    pv_sum = {
        'tee:iffy': 0,
        'tee:mark': 0
    }

    async with AsyncReader(f'{pref}iffy',
                           f'{pref}mark',
                           f'{pref}counter1',
                           f'{pref}counter2',
                           mode="hasty",
                           dwell=0.0) as reader:
        while (time.time()-t0) < 5.0:
            d = await reader.wait_for_incoming()
            print('received:', d)
            received_sum += len(d)
            loop_sum += 1
            for k in pv_sum.keys():
                if k in d:
                    pv_sum[k] += 1

        # need to check that we get half as many "iffy"
        # as we get "mark", because "mark" gets updated twice
        # per IOC loop.
        assert pv_sum['tee:iffy']*2 == pv_sum['tee:mark']

        # we should receive roughly one PV at a time
        # (except for the beginning)
        assert (received_sum - loop_sum) <= 4


async def test_reader_guided(ioc):
    pref = ioc['prefix']
    t0 = time.time()
    data = {}

    received_sum = 0
    loop_sum = 0

    pvlist = (
        f'{pref}iffy',
        f'{pref}jiffy',
        f'{pref}counter1',
        f'{pref}counter2'
    )

    async with AsyncReader(*pvlist,
                           mode="guided",
                           guide_dict={ f'{pref}mark': 0 },
                           dwell=0.0) as reader:
        while (time.time()-t0) < 5.0:
            d = await reader.wait_for_incoming()
            print('received:', [k for k in d.keys()])
            for pv in pvlist:
                ## the first few data sets might not be complete with dwell == 0.0
                if (time.time()-t0) > 1.0:
                    assert pv in d


async def test_reader_thorough(ioc):
    pref = ioc['prefix']
    t0 = time.time()
    data = {}

    received_sum = 0
    loop_sum = 0

    pvlist_ok = [
        f'{pref}iffy',
        f'{pref}jiffy',
        f'{pref}mark',
    ]

    # This one will eventually block, because counterX are not being updated
    pvlist_broken = pvlist_ok + [
        f'{pref}counter1',
        f'{pref}counter2'
    ]

    async with AsyncReader(*pvlist_ok, mode="thorough", dwell=0.0) as reader:
        while (time.time()-t0) < 5.0:
            d = await reader.wait_for_incoming()
            print('received:', [k for k in d.keys()])
            for pv in pvlist_ok:
                assert pv in d

    #async with AsyncReader(*pvlist_broken, mode="thorough", dwell=0.0) as reader:
    #    #with pytest.raises
    #    d = await reader.wait_for_incoming(timeout=3.0)
                


async def test_chain_sloppy(ioc):

    src = EpicsSource(iffy=ioc['prefix']+"iffy",
                      jiffy=ioc['prefix']+"jiffy",
                      mark=ioc['prefix']+"mark",
                      mode='sloppy',
                      dwell=0.2)

    tmax = 5.0
    t0 = time.time()
    elapsed = 0

    #async with PipeExecutor(src) as ex:
    try:
        await src.startup()
        while elapsed < tmax:
            try:
                data, tmp = await asyncio.gather(src(), asyncio.sleep(1.0),
                                                 return_exceptions=False)
                print(f'Received: {[k for k in data]}')
                
                elapsed = time.time()-t0

                assert len(data) == 3
                    

            except Exception as e:
                traceback.print_exc()
                await asyncio.sleep(1.0)
                raise

    finally:
        await src.shutdown()


async def test_chain_guided(ioc):

    pref = ioc['prefix']
    src = EpicsSource(iffy=ioc['prefix']+"iffy",
                      jiffy=ioc['prefix']+"jiffy",
                      guide=f'{pref}mark==0',
                      dwell=0.2)

    tmax = 5.0
    t0 = time.time()
    elapsed = 0

    try:
        await src.startup()
        while elapsed < tmax:
            try:
                data, tmp = await asyncio.gather(src(), asyncio.sleep(1.0),
                                                 return_exceptions=False)
                print(f'Received (guided): {[k for k in data]}')
                
                elapsed = time.time()-t0

                ## tee:mark is going to be missing in guided mode
                assert len(data) == 2
                    

            except Exception as e:
                traceback.print_exc()
                await asyncio.sleep(1.0)
                raise

    finally:
        await src.shutdown()
