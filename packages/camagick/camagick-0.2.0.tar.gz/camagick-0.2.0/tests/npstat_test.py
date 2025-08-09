from camagick.pipe.npfun import Processor as S1Processor

from numpy.random import rand as rand_array

async def test_npstat1():

    func = [
        "mean",
        "average",
        "sum",
        "std"
    ]

    inp = rand_array(17, 43, 59)

    for f in func:
        r1 = await S1Processor(f)({'data': inp})
        for n,d in r1.items():
            print(n, d, d.shape, inp.shape)
