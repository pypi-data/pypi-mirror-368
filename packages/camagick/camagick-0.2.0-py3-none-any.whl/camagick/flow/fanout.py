from camagick.processor import (
    ProcessorBase, FlowBase, SourceBase, SinkBase,
    DuplicateDataTag
)



import asyncio, logging, pprint

logger = logging.getLogger(__name__)

class Processor(FlowBase):
    '''
    Parallel processing of data

    Pipes are run in asynchronously, in parallel. Data outputs of all the branches
    are joined together.

    CLI syntax is { ... } brackets (mind the spaces).
    '''
    
    def __init__(self, *pipes, **kw):
        super().__init__(*pipes)


    async def __call__(self, data=None, context=None):
        logger.debug(f'msg="Fanout" pipes={self.subpipes}')
        out_data = await asyncio.gather(*[p(data, context) for p in self.subpipes],
                                        return_exceptions=False)

        ret = {}
        for o,p in zip(out_data, self.subpipes):

            # Ignore empty results
            if o is None or len(o) == 0:
                continue

            # Don't merge results of sinks into the final data pack.
            # Push them into context instead (ACHTUNG, this might overwrite
            # context information).
            if isinstance(p, SinkBase):
                for k,v in o.items():
                    if k not in context:
                        context[k] = v
                continue

            # make sure we don't overwrite data
            for k in o:
                if k in out_data and out_data[k] is not None:
                    raise DuplicateDataTag(f'msg="Duplicate data tag" tag={k}')

            ret.update(o)

        return ret
