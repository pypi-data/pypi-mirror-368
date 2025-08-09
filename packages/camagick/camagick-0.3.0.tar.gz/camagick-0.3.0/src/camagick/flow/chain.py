from camagick.processor import (
    ProcessorBase, SourceBase, FlowBase, SinkBase,
    DuplicateDataTag
)

import asyncio, logging, pprint

logger = logging.getLogger(__name__)

class Processor(FlowBase):
    '''
    Sequential execution of processors

    For Pipe-type processours, output data from one processor is passed
    as input data to the next. The final data set is returned as a result
    of the chain.
    
    If a given processor is a Source-type, then its output data is rather
    merged into the existing data set instead of fully replacing it.
    '''

    async def __call__(self, data=None, context=None):
        inp = data
        for pipe in self.subpipes:
            outp = await pipe(inp, context)
            if outp is None:
                outp = {}
            logger.debug(f'msg="Chain element" pipe={pipe} '
                         f'in={inp.keys() if inp is not None else None} '
                         f'outp={outp.keys() if outp is not None else None}')

            if isinstance(pipe, SourceBase) and (inp is not None):
                for k,v in outp.items():
                    if k in inp:
                        raise DuplicateDataTag(f'msg="Duplicate tag" tag={k} pipe={pipe}')
                    inp[k] = v
            else:
                inp = outp

        return inp
