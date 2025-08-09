from camagick.pipe.slice import Processor, _parse_slice

from numpy.random import rand as rand_array

async def test_slice():

    sobj = [
        [ slice(10, 15), slice(20,40,2), slice(0,50) ],
        [ None,          slice(20,40,2), slice(0,50) ],
        [ slice(10),     slice(20,40,2), slice(50) ],
        [ 10,            slice(20,40,2), slice(0,50) ],
        [ slice(10, 11), slice(20,40,2), slice(0,50) ],
    ]

    sstr = [
        '10:15,20:40:2,0:50',
        ',20:40:2,0:50',        
        ':10,20:40:2,:50',
        '10,20:40:2,0:50',        
        '10:11,20:40:2,0:50',
    ]

    inp = rand_array(17, 43, 59)

    for so,ss in zip(sobj,sstr):

        tmp = [
            _parse_slice(part) for part in ss.split(',')
        ]
        
        r1 = await Processor(*so)({'data': inp})
        r2 = await Processor(*tmp)({'data': inp})
        
        print(r1.keys(), r1['data'].shape, inp[*so].shape)
        print(ss)        
        print(so)
        print(tmp)

        for a,b in zip(r1.values(), r2.values()):
            assert ((a-b)**2).sum() == 0.0
