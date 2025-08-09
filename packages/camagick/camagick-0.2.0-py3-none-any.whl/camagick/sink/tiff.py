from camagick.processor import SinkBase
import tifffile, logging, traceback, os

## Data sink to store (append) stuff in a HDF5 DataArray

logger = logging.getLogger(__name__)

class Processor(SinkBase):
    def __init__(self, pathfmt: str, start: int = 0, meta: list = None):
        '''
        Saves data into (a series of) TIFF files with dynamic naming.

        Each dataset generates one TIFF file per run. The name and
        path of the TIFF file are generated from scratch on every save,
        so that writing series of files, e.g. with increasing counters,
        is possible.
        
        Args:
            pathfmt: Path format for the tiff file. You can use
              the following variables:
                - `{seq}`: a sequential number (starting with 0 by default),
                  which is being incremented by 1 on every save -- cannot
                  be reset
                - `{suffix}`: the final component (the one after the last ':')
                  of the PV name
                - `{label}`: the key of the data item
                - any key of a data item available in the `context` section
                  of input data
            start: where to start the internal sequential counter

            meta: comma-seprated list of context tags to store in the TIFF
              as metadata. Note that this subject to whatever TiffFile supports.
              This is stored using the `metadata=...` argument to
              `tifffile.imwrite(...)`. So the metadata typically ends up as
              a JSON string on the first page of the Tiff frames object.
              (Load with `frames = tifffile.TiffFile(...)`, and view with
              `frames.pages[0].tags['ImageDescription'].value ...`)
        '''
        super().__init__()
        self.path_fmt = pathfmt
        self.seq = start
        self.meta_tags = meta if meta is not None else []


    def _collect_meta(self, context):
        try:
            meta = {}
            for k in self.meta_tags:
                # Need to convert the type from a numpy data type,
                # to a python type.
                v_raw = context[k]
                if hasattr(v_raw, "shape") and len(v_raw.shape)>0:
                    v_type = type(v_raw.flatten()[0].item())
                    meta[k] = [ v_type(k) for k in v_raw.flatten() ]
                elif hasattr(v_raw, "shape") and len(v_raw.shape)==0:
                    v_type = type(v_raw.flatten()[0].item())
                    meta[k] = v_type(v_raw)
                else:
                    meta[k] = v_raw
            return meta
        except KeyError as e:
            logger.error(f'msg="Data set required as metadata not found" key="{e}"')
            raise RuntimeError(f'Requested metadata {e} not found')


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

        format_params = dict()

        if context is not None:
            format_params.update(context)
        else:
            context = {}

        result = {}
        
        for k,v in data.items():
            path = None
            meta = {}
            try:
                suf = k.split(':')[-1]
                format_params.update(dict(seq=self.seq, suffix=suf, label=k))

                path = self.path_fmt.format(**format_params)

                tfopts = {}

                tfopts.update(dict(compression='zlib'))

                if len(self.meta_tags) > 0:
                    tfopts.update(dict(metadata=self._collect_meta(context)))
                    logger.info('msg="Have metadata" ' +
                                ' '.join([f'{m}={v}' for m,v in tfopts['metadata'].items()]))

                self.ensure_folder_of(path)

                tifffile.imwrite(path, v, **tfopts)
                result[k] = path
                
                #logger.info(f'msg="Writing TIFF" tag="{k}" path="{path}" shape="{v.shape}"')

            except Exception as e:
                traceback.print_exc()
                logger.error(f'msg="Error saving {k}" reason="{e}" shape="{v.shape}" '
                             f'path="{path}" '+
                             ' '.join([f'{ck}="{cv}"' for ck,cv in format_params.items()])+
                             ' '.join([f'{ck}="{cv}"' for ck,cv in meta.items()]))
        
        self.seq += 1

        return result
