from camagick.pipe.npfun import Processor as NpBase

class Processor(NpBase):
    '''
    Short for `--npfun max ...`.
    '''
    def __init__(self, **kw):
        super().__init__("max", **kw)
