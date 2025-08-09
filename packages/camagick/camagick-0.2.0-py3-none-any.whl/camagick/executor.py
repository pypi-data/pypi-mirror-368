import logging, importlib, inspect, pkgutil, typing, types, traceback, asyncio

logger = logging.getLogger(__name__)

from functools import partial
from pprint import pprint, pformat
import numpy as np
from schema import Schema, Or, And, Use, Const, Optional, SchemaError

from camagick.flow.chain import Processor as ChainFlow
from camagick.flow.fanout import Processor as FanoutFlow
from camagick.flow.chain import Processor as ChainFlow
from camagick.probe import opcast, dict_from_str, strip_str

__all__ = [
    "PipeExecutor",
    "PipeValidator",
    "Sequence",
    "SchemaSequenceTooLongError",
    "SchemaSequenceTooShortError",
    "PipeMaker",
    "PipeHelpRequested",
    "find_processors",
    "with_pipe",
    "make_pipe_type",
    "pipe_spec_from_args",
    "QuitApplication",
]

_kind2ymlkey = {
    'sink': 'to',
    'source': 'from',
    'pipe': 'via'
}

_ymlkey2kind = { v:k for k,v in _kind2ymlkey.items() }

class QuitApplication(Exception): pass

class PipeExecutor:
    def __init__(self, flow, warn_residual: bool = False):
        self.flow = flow
        self.warn_residual = warn_residual
        self._ctx_counter = 0


    async def __aenter__(self):
        if self._ctx_counter == 0:
            await self.flow.startup()
            self._task = asyncio.create_task(self.run(startup=False))
        self._ctx_counter += 1
        return self


    async def __aexit__(self, *args):
        self._ctx_counter -= 1
        if self._ctx_counter == 0:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass


    async def step(self):
        context = {}
        out_data = await self.flow(data=None, context=context)
        if (out_data is not None) and len(out_data)>0 and self.warn_residual:
            logger.warning(f'msg="Residual data keys" keys="{out_data.keys()}"')
        return out_data

        
    async def run(self, startup=True):
        
        if startup:
            # If we came here through __aenter__, the flow object should already
            # have been initialized. (Apparently this is necessary to avoid the
            # case where we've entered the 'with' context, but the task wasn't
            # initialized yet.
            # All other cases should not use the 'startup' parameter.
            await self.flow.startup()

        try:
            while True:
                out_data = await self.step()

        except QuitApplication as e:
            logger.info(f'msg="Closing now."')

        except Exception as e:
            traceback.print_exc()
            logger.error(e)
            logger.error('Good bye')

        except KeyboardInterrupt:
            logger.info(f'msg="Good bye."')

        finally:
            logger.info(f'msg="Exector shutting down"')
            await self.flow.shutdown()


def find_processors(base=None, cls=None, full=None, raise_missing=False, noisy_missing=False):
    # Searches a module `base` for Processor submodules
    # (i.e. submodules which have a class named `cls`,
    # typically "Processor").
    #
    # As a convenience, if either `base` or `cls` are not
    # specified, they are read out from `full` first
    # (expected format: "{modbase}.{name}:{cls}")

    if base is None and full is not None:
        ## Split 'full' into its constiuent parts.
        ## Generally, there will only be 1 processor.
        parts = full.split(':')
        if len(parts)>1:
            cls = parts[-1]
        modparts = parts[0].split('.')
        if len(modparts)>1:
            base = modparts[:-2]
            candidates = [modparts[-1]]
        else:
            candidates = [modparts[0]]
    else:
        modbase_obj = importlib.import_module(base)
        candidates = [p.name for p in pkgutil.iter_modules(modbase_obj.__path__)]

    result = {}
    for pname in candidates:

        try:
            if len(base)>0:
                mod_name = f'{base}.{pname}'
            else:
                mod_name = f'{pname}'

            modobj = importlib.import_module(f'{mod_name}')

        except ModuleNotFoundError as e:
            if raise_missing:
                raise
            continue
        except Exception as e:
            if raise_missing:
                raise
            if noisy_missing:
                logger.error(f'msg="Cannot import processor, likely a bug in underlying libraries" name={base}.{pname}')
                logger.error(e)
            continue

        try:
            Cls = getattr(modobj, cls)
            #if not issubclass(Cls, Processor):
            #    continue
        except AttributeError:
            continue

        result[pname] = Cls

    return result
            


def make_pipe_type(kind, name, show_error=True):
    '''
    Returns a Python type for the specified processor.

    Args:
    
        kind: processor kind (one of "sink", "source" or "pipe").
          Currently this is only used for building the internal
          module name. If the module is external, the kind
          parameter is ignored.
    
        name: either a single module name from within `camagick.{kind}.{sub}`,
          or a full Python module name of the format `{module}[:{class}]`,
          where `{module}` may contain several components. The `:{class}`
          part can be omitted if `{module}` contains at least one dot "."
          in which case the class name `Processor` is assumed, similar
          to the built-in processors.
    '''

    mod_cls = name.split(':')

    is_internal = not len(mod_cls)>1
    
    if len(mod_cls) > 1:
        clsname = mod_cls[-1]
    else:
        clsname = "Processor"
        
    try:
        if not is_internal:
            modname = mod_cls[0]
            mod_obj = importlib.import_module(modname)
        else:
            if '.' not in name:
                modname = f'camagick.{kind}.{name}'
            else:
                modname = name
            mod_obj = importlib.import_module(modname)
        cls_obj = getattr(mod_obj, clsname)
        return cls_obj

    except Exception as e:
        if show_error:
            logger.error(f'msg="Error loading processor" name="{name}" '
                         f'module="{modname}.{clsname}')
        raise


def pipe_type_from_node_dict(node):
    key, data = next(iter(node.items()))
    kind = _ymlkey2kind[key]
    return make_pipe_type(kind=kind, name=data[0])


def _type_spec_from_arg(s):
    # Once the leading '--' is removed, 
    # Typical format is either "from-{}", "to-{}" or just plain "{}"
    # for built-in types, and "from=mod.ule[:Object]" or just
    # plain "mod.ule[:Object]" otherwise.
    parts = s.split('-')
    if len(parts) == 2:
        if parts[0] not in ('from', 'to'):
            raise RuntimeError(f'{s}: unknown node kind {parts[0]}')
        return parts
    else:
        return ("via", parts[0])


class PipeHelpRequested(Exception):
    def __init__(self, node):
        self.node = node
        k, n = next(iter(node.items()))
        self.kind = _ymlkey2kind[k]
        self.name = n[0]


def pipe_spec_from_args(args):
    '''
    Makes a pipe spec object from command line arguments
    '''

    node_stack = []
    sequence = None
    node = None
    kkey = None

    pipe = None

    def _open_seq(stack, sname, seq):
        stack.append({ sname: [] })
        if seq is not None:
            seq.append(stack[-1])
        return node_stack[-1][sname]


    def _close_seq():
        node_stack.pop()
        node = node_stack[-1]
        assert len(node) == 1
        k, seq = next(iter(node_stack[-1].items()))
        assert k in ('fanout', 'chain')
        return seq

    sequence = _open_seq(node_stack, 'chain', None)
        
    for a in args:

        if a in ('?', '-?'):
            raise PipeHelpRequested(node)
        
        if a[0:2] == '--':
            # Starting a new node; open a sequence if necessary
            kind, name = _type_spec_from_arg(a[2:])
            #print(f'{kind}.{name} for {sequence}')
            sequence.append({ kind: [ name ] })
            kkey = kind
            node = sequence[-1]
            
        elif a == '{':
            sequence = _open_seq(node_stack, 'fanout', sequence)

        elif a == '[':
            sequence = _open_seq(node_stack, 'chain', sequence)
            
        elif a in ('}', ']'):
            sequence = _close_seq()
            
        else:
            # Regular node argument (positional or keyword)
            #print(a, 'for', node)
            #print('param:', a)
            eq = a.find('=')
            if eq >= 0:
                # Keyword argument
                prm = node.setdefault('params', dict())
                ts = (int, float, dict_from_str, strip_str)
                val = opcast(a[eq+1:], type_sequence=ts)
                #print(a[eq+1:], '->', val, type(val))
                #print(a, ':', a[:eq], '->', a[eq+1:], val, type(val), eq)
                prm[a[:eq]] = val
            else:
                # Positional argument
                node[kkey].append(opcast(a))

    return node_stack[0]


class PipeMaker:
    '''
    Makes a processing pipe out of a valid object representation
    '''
    
    def __init__(self):

        # The type of the current sequence / the sequence that we need
        # to enter on the next __enter__
        self._flow_type = None

        # We always push to the last item of the stack.
        # Initially, this is self._pipes. As we descend into
        # the YAML tree, we add new sequences to the stack, and
        # pop them on every __exit__ (so that the parent sequence
        # captures processors again).
        self._processor_collection_stack = [ (ChainFlow, []) ]

    def __enter__(self, *a, **kw):
        self._processor_collection_stack.append((self._flow_type, []))
        return self


    def __exit__(self, *args):
        level = self._processor_collection_stack.pop()
        flw = level[0](*(level[1]))
        self._processor_collection_stack[-1][-1].append(flw)


    def __call__(self, *args, flow=None):
        ## Args is either sequence-type, or (kind, name, spec)

        if len(args) == 1:
            sequence = args[0]
            self._flow_type = make_pipe_type('flow', sequence)
            return self

        elif len(args) == 3:
            kind, name, spec = args

        # Differentiate between [ "pipe", "arg", ... ]
        # and "pipe": [ "arg", ... ] type of calls.
        a = None
        kw = None
        if isinstance(name, str):
            if isinstance(spec, list):
                a = spec if spec is not None else []
                kw = {}
            elif isinstance(spec, dict):
                a = []
                kw = spec if spec is not None else {}
            elif spec is None:
                a = []
                kw = {}
            else:
                raise RuntimeError(f'{kind}.{name}: invalid args {spec} (of type {type(spec)})')
        else:
            n = name[0]
            a = name[1:]
            name = n
            kw = spec if spec is not None else {}

        astr = ', '.join([f'{k}' for k in a])
        kwstr = ', '.join([f'{k}={v}' for k,v in kw.items()])
        #print(f'{kind}.{name}({astr}, {kwstr})')

        self._processor_collection_stack[-1][-1].append(
            make_pipe_type(kind, name)(*a, **kw)
        )


    @property
    def pipe(self):
        while self._processor_collection_stack:
            level = self._processor_collection_stack.pop()
            self._flw = level[0](*(level[1]))
        return self._flw
            


    def __repr__(self):
        return pformat(self.pipe)


def with_pipe(spec, func, enter=None, exit=None):
    '''
    Walks a pipeline specification structure and calls
    `func(kind, name, params)` for every processing item
    (source, sink or pipe).

    If `enter` and/or `exit` are specified, they're
    expected to contain references to callables of the
    form `proc(sequence_type)`.
    '''

    for item in spec:
        for k in ('chain', 'fanout'):
            if k not in item:
                continue
            v = item[k]
            if hasattr(func, "__enter__"):
                with func(k) as f:
                    with_pipe(v, f)
            else:
                with_pipe(v, func)

        for k in ('from', 'via', 'to'):
            if k not in item:
                continue

            v = item[k]
            func(_ymlkey2kind[k], v, item.get('params', None))



class SchemaSequenceTooShortError(SchemaError): pass

class SchemaSequenceTooLongError(SchemaError): pass


class Sequence(Schema):
    '''
    Custom validator which checks that a list has exactly the
    number (and type) of items it was specified.
    '''

    class VarArguments(Schema):
        '''
        Catch-all for variable-list arguments.
        '''
        pass


    def __init__(self, *items):
        self._items = items


    def __repr__(self):
        si = ', '.join([str(i) for i in self._items])
        return f'{self.__class__.__name__}({si})'


    def validate(self, data):

        #if len(data) > len(self._items):
        #    raise SchemaSequenceTooLongError("too long")

        ditr = iter(data)
        iitr = iter(self._items)
        out = []
        parity = 0
        cnt = 0
        while True:
            try:
                cnt += 1
                i = next(iitr)
                parity += 1
                d = next(ditr)
                parity -= 1
                if not isinstance(i, self.VarArguments):
                    o = Schema(i).validate(d)
                    out.append(o)
                else:
                    # The rest are variable arguments.
                    var_data = [d] + [x for x in ditr]
                    out += i.validate(var_data)
                    break
            except StopIteration as e:
                if parity != 0:
                    # we have fewer data items than data schema items
                    # this means that all schema items from here on
                    # need to be "optional"
                    while True:
                        if not isinstance(i, Optional):
                            raise SchemaSequenceTooShortError(f"{i} at position {cnt} not in data")
                        try: i = next(iitr)
                        except StopIteration: break
                        cnt += 1
                    break
                else:
                    # If we got here, it means that we ran into an StopIteraion at
                    # next(iitr). This is usually the case when we either have too
                    # much data, or when we're at the legit end of a sequence.
                    try:
                        # Try to increment data, too; if this fails, we're at the legit
                        # end of a sequence. If this works, we have too much data.
                        d = next(ditr)
                        raise SchemaSequenceTooLongError(f"too much data at {cnt}")
                    except StopIteration:
                        break

        return out
                
            

class SchemaUnknownPipeError(SchemaError): pass


class PipeValidator(Schema):
    # There are several nasty things going on here.
    #
    # For one, we need recursive validation: our flow elements
    # "chain" and "fanout" contain a list of what would be pipe
    # elements, or other flow elements! Schema() doesn't seem to
    # have an obvious way to do this, so we're going to do a little
    # hack and actually register the class's .validate() function
    # as an evaluator callable for the contents of the flow elements'
    # list.
    #
    # Then there's the issue with the pipe elements: these may contain
    # a "params" key with a dictionary, but the contents of that
    # dictionary are specific to the actual pipe elemen we're going
    # to use. So in order to _actually_ validate, we need to load
    # the module and ask the pipe element class (either through
    # built-in validation info, or through type hint introspection
    # into the pipe class's .__init__() callable.
    # But in order to do this at "params" evaluation time, we
    # actually need to know which class we're talking about -- which
    # is specified in the previous dict item
    # ("from", "via", "to" -> name).
    #
    # So we actually have two ways of doing this:
    #
    #  - One is by replacing the whole sequence with a callable.
    #    This has the benefit of working with any kind of modules,
    #    even external ones, because the evaluation takes place
    #    at execute-time.
    #
    #  - The other is by generating a list of items from
    #    `camagick.pipe` and actually putting together all of the
    #    pipe elements. This has the advantage of generating a
    #    more-or-less static list (at runtime, though), but it
    #    won't properly validate pipe elements from extrnal modules
    #    unknown to camagick. :-/
    #
    # Pick one.

    def __init__(self, other_pipes=None, example=None, **kwargs):

        self.param_validators = self._builtin_validators()

        super().__init__(
            # FIXME: the first part (validate_processor) is a horrible mix
            # of dynamic validation through function call, and a static
            # validation against a statically-built name/kind dependent
            # scheme ("param_validators").
            # This is because we have a funny format when it comes to
            # mixing positional/keyword parameters.
            # Need to rip that apart ASAP and make it more declarative.
            Or(self._validate_processor, {Or("chain", "fanout"): [self.validate]}),
            **kwargs
        )

    def __repr__(self):
        return 'PipeValidator'


    def _builtin_validators(self):
        # Returns the list of validators for built-in types.
        
        # A processor spec can be of different types:
        #
        # a) only-keyword-parameter tupe:
        #    { "from|via|to": "name"
        #      "params": { "key": value, ...} }
        #
        # b) only-positional-parameter type:
        #    { "from|via|to": "name"
        #      "params": [ value, ... ] }
        #
        # c) short-hand mix positional / keyword parameter:
        #    { "from|via|to": [ "name", value, ... ]
        #      "params": { "key": another_value, ... } }
        #        

        self.processors = {}
        param_validators = {}
        for kind in ("source", "sink", "pipe"):
            self.processors[kind] = find_processors(base=f'camagick.{kind}',
                                                    cls='Processor')
            
            param_validators[kind] = {
                name:self._make_params_validator(Cls, kind, name) \
                for name,Cls in self.processors[kind].items()
            }
            
        return param_validators


    def _kind_and_nameline(self, data):
        # this is the "via": ... line.
        # the ... part can either be a string (name only), or
        # an array of [name, *positional_params].
        name = None
        for k in ("from", "via", "to"):
            if k in data:
                name = data[k]
                break

        if name is None:
            raise SchemaUnknownPipeError('/'.join(data.keys()))
        
        return (_ymlkey2kind[k], name)


    def _validate_processor(self, data):

        kind, nameline = self._kind_and_nameline(data)
        if isinstance(nameline, list):
            name = nameline[0]
            if len(nameline)>1:
                params = nameline[1:]
            else:
                params = {}
        else:
            name = nameline
            params = data.get('params', {})

        try:
            scm = self.param_validators[kind][name]
        except KeyError:
            raise SchemaUnknownPipeError(f'Unknown pipe "{name}" '
                                         f'of kind "{kind}"')

        return {_kind2ymlkey[kind]: name, 'params': scm.validate(params)}


    def _make_params_validator(self, Class, kind, name):
        # This returns either a list, or a dictionary, of Schema components
        # able to validate a parameter list intended for Class().
        #
        # The difficulty is that Unlike in Python, for YAML/JSON we need to
        # settle either _lists_ or _dict_ -- no mixing.
        # This means that we either have positional only, or keyword-only
        # arguments (in both cases also considering optional arguments).
        #
        # We need to determine:
        #
        #  - is either possible (dict or list), or is only one allowed?
        #    -> Any POSITIONAL_ONLY present in the annotations without default
        #       value means automatically that we need to go for a list;
        #    -> Same with KEYWORD_ONLY without default value -> need dict.
        #       (If both are the case, we raise an error.)
        #  
        # - are there mandatory arguments (of any kind)? 
        #    -> Generally, all arguments without a default value are mandatory (right?)        
        
        sig = inspect.signature(Class).parameters

        # Lists of argument spec tuples (name, obj)

        # These can be only positional -- mandatory arguments.
        pos_only = [i for i in filter(lambda x: x[1].kind in \
                                      (x[1].POSITIONAL_ONLY, x[1].VAR_POSITIONAL),
                                      sig.items())]

        # These can be only keyword-based -> optional arguments.
        key_only = [i for i in filter(lambda x: \
                                      x[1].kind in (x[1].KEYWORD_ONLY, x[1].VAR_KEYWORD),
                                      sig.items())]

        # Keywords or positional -> optional, but must be listed (as optional)
        # in the accepted list of positional arguments, too.
        pok      = [i for i in filter(lambda x: x[1].kind == x[1].POSITIONAL_OR_KEYWORD, sig.items())]

        # Positional, Mandatory: all positional arguments, no default value
        pos_mandatory = \
            [i for i in pos_only] + \
            [i for i in filter(lambda x: x[1].default == x[1].empty, pok)]

        # Positional, Optional: all other positional arguments (are there any?),
        # and all key-or-positional arguments which have a default value.
        pos_optional = \
            [i for i in filter(lambda x: x[1].default != x[1].empty, pos_only)] + \
            [i for i in filter(lambda x: x[1].default != x[1].empty, pok)]

        # Keyword, Mandatory: are there any _mandatory_ keyword arguments?...
        key_mandatory = []

        # Keyword, Optional: all pok, and all key arguments
        key_optional = \
            [i for i in filter(lambda x: x[1].default != x[1].empty, pok)] + \
            [(str, i[1]) for i in key_only]

        # Returns a usable type (either the annotation, if it is a single type; or 'object')
        # Ideally we'd like to return the individual types of the annotation UnionType here,
        # but I don't know of any elegant way of doing that :-(
        determine_type = \
            lambda x: ((x.annotation if x.annotation is not x.empty else object) \
            if (typing.get_origin(x.annotation) is None) else object) \
               if (x.kind != x.VAR_POSITIONAL) else Sequence.VarArguments([object])


        positional = \
            [ determine_type(pspec)           for pname,pspec in pos_mandatory  ] + \
            [ Optional(determine_type(pspec)) for pname,pspec in pos_optional ]

        keyword = { pname:determine_type(pspec) for pname,pspec in key_mandatory+pos_mandatory }
        keyword.update({ Optional(pname):determine_type(pspec) \
                         for pname,pspec in key_optional  })

        #print(f'{kind}.{name}: Positional:', pformat(positional))
        #print(f'{kind}.{name}: Keyword:', pformat(keyword))

        return Or(Sequence(*positional), keyword)
