from camagick.processor import ProcessorBase
import re

class Processor(ProcessorBase):    
    '''
    Renames data tags.
    '''

    def __init__(self, fmt: str, only: str = ''):
        '''
        Args:
            fmt: new tag format. Use `{}` or `{tag}` to fill in the
              old tag names, or any context key for the corresponding
              context data.

            only: if set to a non-empty string, only tags matching this
              regex pattern are renamed.
        '''

        self._format = fmt
        self._only = re.compile(only) if len(only)>0 else None

    
    async def __call__(self, data=None, context=None):

        if data is None:
            return None

        matcher = lambda x: \
            (self._only is None) or \
            (self._only.match(x[0]) is not None)

        output = {
            self._format.format(tag, tag=tag, **context):val \
            for tag, val in filter(matcher, data.items())
        }
        
        output.update({
            tag:val for tag, val in filter(lambda x: not matcher(x), data.items())
        })

        return output
