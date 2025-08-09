import pytest, asyncio, time, traceback
import multiprocessing as mp

from camagick.source.scratch import Processor as GenSource
from camagick.source.ioc import Processor as IocSource
from camagick.source.epics import Processor as EpicsSource

from camagick.sink.ioc import Processor as IocSink
from camagick.sink.epics import Processor as EpicsSink
from camagick.sink.summary import Processor as SummarySink

from camagick.sink.hdf5 import Processor as Hdf5Sink

from camagick.flow.chain import Processor as ChainFlow
from camagick.flow.fanout import Processor as FanoutFlow

from camagick.pipe.pace import Processor as Pace
from camagick.pipe.only import Processor as Only
from camagick.pipe.exclude import Processor as Exclude

from camagick.executor import PipeExecutor

import tempfile, os, random, h5py
import numpy as np

@pytest.fixture(scope='function')
def h5tmp():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    yield tmp.name
    os.unlink(tmp.name)
    

async def test_h5_append(h5tmp):

    print(f"HDF5: {h5tmp}")

    h5_path = f'{h5tmp}#group'+'{gi}/{tag}{di}'

    sink = Hdf5Sink(h5_path, index='idx')

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

    with h5py.File(h5tmp, 'r') as h5:
        assert (h5['/group0/scalar10'][()] == scalar[0:10:2]).all()
        assert (h5['/group0/array10'][()]  ==  array[0:10:2]).all()
        assert (h5['/group1/scalar10'][()] == scalar[1:10:2]).all()
        assert (h5['/group1/array10'][()]  ==  array[1:10:2]).all()
        
        assert (h5['/group0/scalar20'][()] == scalar[10::2]).all()
        assert (h5['/group0/array20'][()]  ==  array[10::2]).all()
        assert (h5['/group1/scalar20'][()] == scalar[11::2]).all()
        assert (h5['/group1/array20'][()]  ==  array[11::2]).all()


async def test_h5_overwrite(h5tmp):
    print(f"HDF5: {h5tmp}")

    sink = Hdf5Sink(h5tmp, index='idx', mode='o')

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
        

    with h5py.File(h5tmp, 'r') as h5:
        assert (h5['/array'][()] == array[half_pts:]).all()
    

    # since we didn't specify the top-up '+' flag,
    # writing beyond the end of the dataset should raise
    with pytest.raises(RuntimeError):
        await sink(data={'array': array[0]},
                   context={'idx': half_pts+2})


async def test_h5_reset(h5tmp):
    print(f"HDF5: {h5tmp}")

    sink = Hdf5Sink(h5tmp, index='idx', mode='x')

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
        

    with h5py.File(h5tmp, 'r') as h5:
        assert h5['/array'].shape[0] == 5
        assert (h5['/array'][()] == array[half_pts:half_pts+5]).all()
    

    # since we didn't specify the top-up '+' flag,
    # writing beyond the end of the dataset should raise
    with pytest.raises(RuntimeError):
        await sink(data={'array': array[0]},
                   context={'idx': half_pts+2})
