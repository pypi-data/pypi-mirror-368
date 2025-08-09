from camagick.processor import ProcessorBase
import numpy as np


def _parse_slice(s):
    parts = s.split(':')
    
    if len(parts)==1:
        return None if len(parts[0])==0 else int(parts[0])

    if len(parts) > 0:
        sparam = [int(p) if len(p)>0 else None for p in parts]
        return slice(*sparam)

    raise RuntimeError('Why are we here?')


class Processor(ProcessorBase):    
    '''
    Slices, a.k.a. selects, a subset of each dataset.
    '''

    def __init__(self, *rois):
        '''
        Iteratively selects regions of interests from data.

        Args:
            *rois: each unnamed parameter is either a `slice()`
              object, a string of the format "start:stop:step"
              or "index", or `None`. If it's a string, a slice
              object is constructed from the parsed string values.
              If it's `None`
        '''

        if len(rois)==1 and isinstance(rois[0], str):
            r = rois[0].split(',')
            rois = r

        # ROI tag. Will be used for naming the output data, defaults to "roi"
        #self.roi_tag = tag if tag is not None else "roi"

        # ROR params, one for each dimension.
        self.roi_params = []
        for r in rois:
            if type(r) in (type(None), int, type(slice(0))):
                self.roi_params.append(r)
            elif isinstance(r, str):
                self.roi_params.append(_parse_slice(r))
        
    
    async def __call__(self, data=None, context=None):
        ''' Executes the ROI selection. Context is ignored. '''
        try:
            return {
                key:val[*self.roi_params] for key,val in data.items()
            }
        except Exception as e:
            print("ROI:", self.roi_params)
            print("Data:", data)
            raise
