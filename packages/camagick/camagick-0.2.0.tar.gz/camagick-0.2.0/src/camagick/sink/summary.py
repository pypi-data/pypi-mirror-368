from camagick.processor import ProcessorBase, SinkBase

import sys

class Processor(SinkBase):
    '''
    Outputs a human-readable data summary.

    Generally, the intention is to print the data itself, as it's the
    most self-explanatory form -- but only with scalar data :-)
    For complex data types (e.g. arrays), we display a short message
    notifying _that_ it's an array, and the shape and data type it has.

    We call this "the information".
    '''
    
    def __init__(self, mode: str = 'block', fmt: str = '{tag}: {}', path: str = '-'):
        '''
        Args:
            mode: output mode, choose between 'block' or 'table'.
              In `block` mode, essentially every line is one data set,
              i.e. the complete data payload of one pipeline frame is
              displayed as a "block". The format of each block line is
              specified by `fmt`.

              In `table` mode, the keys are printed first as a header of
              sorts, and the data information is printed per-round as
              a single tab-separated line, one line per frame.

            fmt: Format of a block line, default is `{tag}: {}`, where
              `{}` is substituted by the data representation (mostly
              it's a value if the value is compact; for arrays, it's
              the shape of the array and the data type).

            path: where to write the data. If empty string '', or '-'
              data is written to `stdout`. Otherwise writing to the specified
              file is attempted.
        '''

        self._mode = mode
        self._blk_fmt = fmt
        self._path = path
        self._header_list = []

        self._current_file = None


    def value_repr(self, v):
        if hasattr(v, "shape"):
            if (len(v.shape)>1) or \
               (len(v.shape)==1 and v.shape[0]>1):
                dt = type(v.flatten()[0].item())
                return f'shape={v.shape} {dt}'
            else:
                return str(v)
                
        else:
            return f'{v}'
        

    def ensure_header(self, fobj, data):
        for h in self._header_list:
            if h not in data:
                self._header_list = [k for k in data]
                self.ensure_header(fobj, data)
                fobj.write('#' + '\t'.join([k for k in data])+'\n')

        for k in data:
            if k not in self._header_list:
                self._header_list = [k for k in data]
                self.ensure_header(fobj, data)
                fobj.write('# ' + '\t'.join([k for k in data])+'\n')

        return None


    def write_data(self, fobj, data, context):
        if self._mode in ('block'):
            for k,v in data.items():            
                fobj.write(self._blk_fmt.format(self.value_repr(v),
                                                tag=k, **context)+'\n')
            return
        
        if self._mode in ('table'):
            self.ensure_header(fobj, data)
            fobj.write('\t'.join([
                self.value_repr(data[k]) for k in self._header_list
            ])+'\n')
            return

        raise RuntimeError(f'msg="Unknown summary mode" mode={self._mode}')


    def reset_output(self):
        self._header_list = []


    def ensure_folder_of(self, path):
        d = os.path.dirname(path)
        if not os.path.exists(d):
            os.makedirs(d)
            return
        if not os.path.isdir(d):
            raise RuntimeError(f'msg="Path is required to be a folder folder" path="{p}"')        
        
    
    async def __call__(self, data=None, context=None):
        if data is None:
            return

        if self._path in ('', '-'):
            self.write_data(sys.stdout, data, context)

        else:

            p = self._path.format(**context)
            if self._current_file != p:
                self._current_file = p
                self.reset_output()

            self.ensure_folder_of(p)

            with open(p, 'ta+') as fobj:
                self.write_data(fobj, data, context)
