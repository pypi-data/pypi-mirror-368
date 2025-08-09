#!/usr/bin/python3

import os, time, asyncio, sys, logging, argparse, traceback, yaml,\
    pprint

from camagick.executor import PipeExecutor, PipeMaker, PipeValidator, \
    with_pipe, pipe_spec_from_args, find_processors, PipeHelpRequested, \
    make_pipe_type, pipe_type_from_node_dict

from camagick import _version

logger = logging.getLogger("camagick")

from camagick.probe import strip_str

yaml.SafeDumper.add_representer(strip_str, lambda d, s: d.represent_str(str(s)))

class CAspyApplication:
    def __init__(self, *executors, argv=None, env=None):

        self._argv = argv if argv is not None else sys.argv
        self._env = env if env is None else os.environ.copy()

        self._setup_logging()

        if len(executors) > 0:
            self.executors = executors
        else:
            self.executors = self._handle_args(self._argv[1:])


    def _handle_args(self, args):
        opts, pipe_args = self._parse_cmdline(args)
        self._maybe_help(opts)

        def _title(l, default=''):
            if l[1] == '':
                return l[0]
            else:
                return default
                
        def _body(l):
            if l[1] == '':
                return l[2:]
            else:
                return l

        def _underline(txt, char='='):
            return ''.join(([char]*len(txt)))+'\n'

        def _format_body(ilines):
            olines = []
            new_paragraph = None
            for l in ilines:

                if len(l.strip()) == 0:
                    new_paragraph = True
                    olines.append('')
                    continue
                
                if l[0] not in (' ', '\t') and \
                   l[-1]==':' and \
                   new_paragraph == True:
                    olines.append(f'## {l[:-1]}\n')
                    continue
 
                new_paragraph = False               
                olines.append(l)

            return '\n'.join(olines)
        
        try:
            spec = self._obtain_spec(opts, pipe_args)
            self._maybe_save_spec(opts, spec)
            pipe = self._pipe_from_spec(spec)
            return [PipeExecutor(pipe)]

        except PipeHelpRequested as ph:
            ntype = pipe_type_from_node_dict(ph.node)
            d1 = ntype.__doc__
            if hasattr(ntype, "__init__"):
                d2 = ntype.__init__.__doc__

            head = f'Using The "{ph.name}" {ph.kind.title()}-Processor'
            print(head)
            print(_underline(head, '='))
            for def_title,doc in (('General Information', ntype.__doc__),
                                  ('Initialization', ntype.__init__.__doc__),
                                  ('', ntype.__call__.__doc__)):
                if doc is None:
                    continue

                lns = doc.split('\n')
                if len(lns[0]) == 0:
                    del lns[0]
                t = _title(lns, default=def_title)
                print(t)
                print( _underline(t, '-') )
                print( _format_body((_body(lns))) )

            sys.exit(0)


    def _maybe_help(self, opts):
        if opts.list_all:
            self._print_flow()
            sys.exit(0)


    def _obtain_spec(self, opts, pipe_args):
        if opts.yaml:
            filename = '/dev/stdin' if opts.yaml == '-' else opts.yaml
            with open(filename, 'r') as f:
                raw_spec = yaml.safe_load(f)
        else:
            raw_spec = pipe_spec_from_args(pipe_args)

        return self._validate_spec(raw_spec)


    def _maybe_save_spec(self, opts, spec):
        if opts.save:
            print(yaml.safe_dump(spec))
            sys.exit(0)


    def _parse_cmdline(self, args):
        self._par = argparse.ArgumentParser(
            prog="caspy",
            usage="%(prog)s [options] <pipe>",
            description="Swiss Army Knife for scientific data collection.",
            epilog="Try `-list-all` for a list of processors."
        )

        self._par.add_argument('-version', action='version', version=_version.version,
                               help="prints version information and exits")
        self._par.add_argument('-list-all', action="store_true",
                               help="list available data flow and processing pipe modules")
        self._par.add_argument('-save', action="store",
                               help="don't execute the pipeline, just dump command line "
                               "arguments as YAML to stdout")
        self._par.add_argument('-yaml', action="store",
                               help="load processing pipeline from YAML file")

        _opts, _pargs = self._par.parse_known_args(args)
        
        return _opts, _pargs
    

    def _print_flow(self):

        mod_dict = {}
        max_len = 0

        print('Collecting information about available processors...')
        
        for ft in ('flow', 'source', 'sink', 'pipe'):
            proc_dict = find_processors(f'camagick.{ft}', 'Processor',
                                        noisy_missing=True)
            mod_dict[ft] = proc_dict
            max_len = max(max_len, *[len(i) for i in proc_dict])

        print()

        hints = {
            'source': ' (use as `--from-<name> ...`)',
            'sink':   ' (use as `--to-<name> ...`)',
            'pipe':   ' (use as `--<name> ...`)',
            'flow':   ' (mind the bracket syntax)'
        }        
        
        for ft, pipes in mod_dict.items():            
            
            print(f'{ft} processors{hints[ft]}:\n')
            for pname, pobj in pipes.items():

                docstr = pobj.__doc__ if pobj.__doc__ is not None else pobj.__init__.__doc__
                if docstr is not None:
                    parts = docstr.split("\n")
                    short = next(iter(filter(lambda x: len(x) > 0, parts)))
                else:
                    short = "(no documentation available)"

                fmt = '  {name:' + f'{max_len}' + '}  {short}'
                print(fmt.format(name=pname, short=short))
            print('\n')

        print('Try `--<processor> ?` for detailed processor-specific help.')

        
    def _setup_logging(self):
        logging.basicConfig()
        logger.setLevel(self._env.get("CASPY_LOG_LEVEL", "WARNING"))


    def _validate_spec(self, raw_spec):
        val = PipeValidator()
        return val.validate(raw_spec)


    def _pipe_from_spec(self, spec, validate=True):
        if validate:
            s = self._validate_spec(spec)
        else:
            s = spec
        pm = PipeMaker()
        with_pipe([s], pm)
        return pm.pipe
        
        
    async def run(self):
        await asyncio.gather(*[e.run() for e in \
                               filter(lambda x: x is not None,
                                      self.executors)],
                             return_exceptions=False)


def main(args=None, env=None):

    if args is None:
        args = sys.argv

    if env is None:
        env = os.environ.copy()

    app = CAspyApplication(argv=args, env=env)

    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        logger.info(f'msg="Good bye."')


if __name__ == "__main__":
    main()
