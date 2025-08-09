import pytest, asyncio, time, traceback
import multiprocessing as mp

from camagick.source.scratch import Processor as GenSource
from camagick.source.ioc import Processor as IocSource
from camagick.source.epics import Processor as EpicsSource

from camagick.sink.ioc import Processor as IocSink
from camagick.sink.epics import Processor as EpicsSink
from camagick.sink.summary import Processor as SummarySink

from camagick.sink.zarr import Processor as ZarrSink

from camagick.flow.chain import Processor as ChainFlow
from camagick.flow.fanout import Processor as FanoutFlow

from camagick.pipe.pace import Processor as Pace
from camagick.pipe.only import Processor as Only
from camagick.pipe.exclude import Processor as Exclude

from camagick.executor import PipeExecutor

import tempfile, os, random, zarr
import numpy as np

@pytest.fixture(scope='function')
def ztmp():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    os.unlink(tmp.name)
    yield tmp.name
    #os.unlink(tmp.name)
    pass

async def test_z_append(ztmp):

    print(f"Zarr: {ztmp}")

    z_path = f'{ztmp}#group'+'{gi}/{tag}{di}'

    sink = ZarrSink(z_path, index='idx', mt=False)

    nr_pts = 20
    scalar = np.random.random((nr_pts,))
    array = np.random.random((nr_pts, 23))

    for i in range(nr_pts):
        await sink(
            data={
                'scalar': scalar[i],
                'array':  array[i]
            },
            context={
                'gi': i % 2,
                'di': (int(i/10)+1)*10,
                'idx': int(i/2) % 5
            })

    zf = zarr.open_group(f'{ztmp}', mode='r')
    print('groups:', [g for g in zf.groups()])

    zf0 = zarr.open_group(f'{ztmp}', path='group0', mode='r')
    zf1 = zarr.open_group(f'{ztmp}', path='group1', mode='r')

    print('groups:', [g for g in zf0.groups()] + [g for g in zf1.groups()])
    print('arrays:', [a for a in zf0.arrays()])
    print('arrays:', [a for a in zf1.arrays()])

    assert (zf0['scalar10'][()] == scalar[0:10:2]).all()
    assert (zf0['array10'][()]  ==  array[0:10:2]).all()
    assert (zf0['scalar20'][()] == scalar[10::2]).all()
    assert (zf0['array20'][()]  ==  array[10::2]).all()
    
    assert (zf1['scalar10'][()] == scalar[1:10:2]).all()
    assert (zf1['array10'][()]  ==  array[1:10:2]).all()
    assert (zf1['scalar20'][()] == scalar[11::2]).all()
    assert (zf1['array20'][()]  ==  array[11::2]).all()


async def test_z_overwrite(ztmp):
    print(f"Zarr: {ztmp}")

    sink = ZarrSink(ztmp, index='idx', mode='o', mt=False)

    nr_pts = 20
    half_pts = int(nr_pts/2)
    array = np.array([[i+j*10 for i in range(6)] for j in range(nr_pts)])

    for i in range(half_pts):
        await sink(
            data={ 'array': array[i] },
            context={ 'idx': i })

    for i in range(half_pts):
        await sink(
            data={ 'array': array[i+half_pts] },
            context={ 'idx': i })

    zf = zarr.open_group(f'{ztmp}', mode='r')
    print('groups:', [g for g in zf.groups()])
    print('arrays:', [a for a in zf.arrays()])
    
    assert (zf['array'][()] == array[half_pts:]).all()

    # since we didn't specify the top-up '+' flag,
    # writing beyond the end of the dataset should raise
    with pytest.raises(RuntimeError):
        await sink(data={'array': array[0]},
                   context={'idx': half_pts+2})


async def test_z_reset(ztmp):
    print(f"Zarr: {ztmp}")

    sink = ZarrSink(ztmp, index='idx', mode='x', mt=False)

    nr_pts = 20
    half_pts = int(nr_pts/2)
    array = np.array([[i+j*10 for i in range(6)] for j in range(nr_pts)])

    for i in range(half_pts):
        await sink(
            data={ 'array': array[i] },
            context={ 'idx': i })

    for i in range(5):
        await sink(
            data={ 'array': array[half_pts+i] },
            context={ 'idx': i })
        

    zf = zarr.open_group(f'{ztmp}/', mode='r')
    print('groups:', [g for g in zf.groups()])
    print('arrays:', [a for a in zf.arrays()])    
    assert zf['array'].shape[0] == 5
    assert (zf['array'][()] == array[half_pts:half_pts+5]).all()
    

    # since we didn't specify the top-up '+' flag,
    # writing beyond the end of the dataset should raise
    with pytest.raises(RuntimeError):
        await sink(data={'array': array[0]},
                   context={'idx': half_pts+2})
