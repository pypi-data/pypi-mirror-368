from camagick.executor import PipeExecutor
from camagick.storage.memory import ArrayAccess as MemoryArrayAccess

import tempfile, os, random, h5py, pytest, pprint, importlib
import numpy as np

for mod in ('astor',):
    name_here = mod[0].upper()+mod[1:]
    base = importlib.import_module(f'camagick.source.{mod}')
    globals()[name_here] = getattr(base, 'Processor')

@pytest.fixture()
def rndata():
    return np.random.rand(30, 36, 72)

@pytest.fixture()
def h5tmp(rndata):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    with h5py.File(tmp.name, 'a') as h5:
        grp = h5.create_group('/group')
        grp.attrs['gmeta'] = 'group'
        data = grp.create_dataset(data=rndata, name='data')
        data.attrs['dmeta'] = 'dataset'
    yield tmp.name
    #os.unlink(tmp.name)


async def test_astor(h5tmp, rndata):

    ast = Astor(
        h5tmp,
        kind='hdf5',
        full='/group/data',
        part='/group/data[1:10:2,10:30]',
        dmeta='/group/data.attrs[dmeta]',
        gmeta='/group.attrs[gmeta]',
        dshape='/group/data.shape',
        dlist='/group.keys',
        root='.keys'
    )
    data = await ast()

    assert (data['full'] == rndata).all()
    assert (data['part'] == rndata[1:10:2,10:30]).all()
    assert data['dshape'] == rndata.shape
    assert data['dmeta'] == 'dataset'
    assert data['gmeta'] == 'group'
    assert data['dlist'][0] == 'data'
    assert 'group' in data['root']


async def test_array_store():
    s1 = MemoryArrayAccess("testarray",
                           mode='a+',
                           d1="group/data1",
                           d2="group/sub/data2")

    async with s1:
        for i in range(10):
            await s1.push_frame(i,
                                d1=np.array([1*i, 2*i, 3*i]),
                                d2=np.array(3.14*i))

    pprint.pprint(s1._repo._storage)
    
