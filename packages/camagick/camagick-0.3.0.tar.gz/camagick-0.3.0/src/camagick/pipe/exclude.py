
from camagick.pipe.only import _FilterBase

class Processor(_FilterBase):
    '''
    Blacklist-based data blocker -- allows only named data to pass.

    Blocks data items with keys that match any
    of the regex expressions. The match is case-sensitive.
    '''
    def __init__(self, *items: list):
        super().__init__(False, *items)
