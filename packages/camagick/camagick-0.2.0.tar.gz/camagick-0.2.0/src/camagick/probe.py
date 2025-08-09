
__all__ = [
    "make_probe"
]

class dict_from_str(dict):
    # Dirty way to convert a command-line string (foo=var,foo2=var2,...)
    # into a dict.
    def __init__(self, from_str):
        super().__init__()
        s = from_str

        if s[0] == '"' and s[-1] == '"':
            raise ValueError(f'refusing to parse quoted string')
       
        while True:
            i = s.find(',')
            if (i < 0):
                if len(s) == 0:
                    break
                else:
                    i = len(s)

            param = s[:i]

            j = param.find('=')
            if j < 0:
                raise ValueError(f'not a dict: {from_str}')
            key = opcast(param[:j])
            val = opcast(param[j+1:])

            self[key] = val

            s = s[i+1:]


class strip_str(str):
    def __new__(cls, s):
        if s[0] == '"' and s[-1] == '"':
            return super().__new__(cls, s[1:-1])
        else:
            return super().__new__(cls, s)
 

def opcast(s, type_sequence=None):
    '''
    Opportunistic cast.

    Tries to convert `s` into a "higher quality"
    data type by attempting a cast to the types in `type_sequence`.
    If a `ValueError` is received, subsequent types are tried
    until the list is empty.
    If none matches, return `None`.
    The final element should be a `str` if you want to avoid `None`
    casts.    

    Args:
        s: the data, preferrably as string
        type_sequence: tuple of types to try, by default `(int, float, str)`.

    Returns: the same data as `s` just with a "better" type (if successful),
      or `None` if no conversion could be done.
    '''

    if type_sequence is None:
        type_sequence = (int, float, str)

    for Tp in type_sequence:
        try: return Tp(s)
        except (ValueError, TypeError): continue

    return None


class ValueDisconnected(Exception): pass


class _value_probe:
    def __init__(self, tag):
        self._tag = tag

class _EpicsValue_ophyd(_value_probe):
    rank = 0
    pref = '€'
    def __init__(self, pv):
        self._pv = pv[1:] if pv[0] == '€' else pv

        # pyepics apparently stumbles over empty strings. One possibility
        # how we deal with it is to query the string directly, and try to
        # do our own poor-man's conversion.
        from ophyd.signal import EpicsSignalRO
        self._sig = EpicsSignalRO(self._pv, name="value", string=True)
        self._latest_value = None
        
    def __call__(self):
        self._latest_value = opcast(self._sig.get())
        return self._latest_value


    def __repr__(self):
        s = f'€{self._pv}'
        if self._latest_value is not None:
            s += '{'+f'{self._latest_value}'+'}'
        return s


class _EpicsValue_caproto(_value_probe):
    rank = 0
    pref = '€'
    def __init__(self, pv):
        # This only works within an asyncio loop.
        self._pv = pv[1:] if pv[0] == '€' else pv

        from ophyd.signal import EpicsSignalRO
        self._sig = EpicsSignalRO(self._pv, name="value", string=True)
        self._latest_value = None
        
    def __call__(self):
        tmp = self._sig.get()
        try:
            self._latest_value = int(tmp)
        except ValueError:
            try:
                self._latest_value = float(tmp)
            except ValueError:
                self._latest_value = str(tmp)
        return self._latest_value


    def __repr__(self):
        s = f'€{self._pv}'
        if self._latest_value is not None:
            s += '{'+f'{self._latest_value}'+'}'
        return s


EpicsValue = _EpicsValue_ophyd


class EnvValue(_value_probe):
    rank = 0
    pref = '$'
    def __init__(self, env):
        self._env = env

    def __call__(self):
        from os import environ


class Value(_value_probe):
    rank = 0
    pref = None
    def __init__(self, val):
        if val in ["true", "false"]:
            self._v = val == "true"
        else:
            try:
                self._v = int(val)
            except ValueError:
                try:
                    self._v = float(val)
                except ValueError:
                    self._v = str(val)


    def __call__(self): return self._v
    def __repr__(self): return str(self._v)


class _unary_probe:
    def __init__(self, other):
        self._o = other
    def __repr__(self):
        return f"{self.marks[0]}({self._o})"

class Not(_unary_probe):
    rank = 6
    marks = [ "!", "-n" ]
    def __call__(self): return not self._o()

class Inv(_unary_probe):
    rank = 10
    marks = [ "-", "-i" ]    
    def __call__(self): return  -1*self._o()


class Empty(_unary_probe):
    rank = 8
    marks = [ "^", "-z" ]
    def __call__(self):
        print(f'Empty probe: {self._o()}')
        return len(self._o()) == 0

    
class _binary_probe:
    def __init__(self, l, r):
        (self._l, self._r) = (l, r)

    def __repr__(self):
        return f"({self._l}{self.marks[0]}{self._r})"


class Eq(_binary_probe):
    rank = 8
    marks = [ "==", "-eq" ]
    def __call__(self): return self._l() == self._r()


class Neq(_binary_probe):
    rank = 8
    marks = [ "!=", "-ne" ]
    def __call__(self): return self._l() != self._r()

class Lt(_binary_probe):
    rank = 8
    marks = [ "<", "-lt" ]
    def __call__(self): return self._l() < self._r()

class Leq(_binary_probe):
    rank = 8
    marks = [ "<=", "-le" ]
    def __call__(self): return self._l() < self._    
    
class Gt(_binary_probe):
    rank = 8
    marks = [ ">", "-gt" ]
    def __call__(self): return self._l() < self._r()

class Geq(_binary_probe):
    rank = 8
    marks = [ ">=", "-ge" ]
    def __call__(self): return self._l() < self._r()

class And(_binary_probe):
    rank = 4
    marks = [ "&&", "-a" ]
    def __call__(self): return (self._l() and self._r())


class Or(_binary_probe):
    rank = 2
    marks = [ "||", "-o" ]
    def __call__(self): return (self._l() or self._r())


import inspect

#
# building all_probes dictionary (look up all _binary_probe and
# _unary_probe classes in this module).
# 
all_probes = {}
_probes = {
    k:v for k, v in globals().items() \
    if (inspect.isclass(v) and \
        (issubclass(v, _unary_probe) or \
         issubclass(v, _binary_probe)) and \
        v not in (_unary_probe, _binary_probe))    
}
for k,v in _probes.items():
    for m in v.marks:
        all_probes[m] = v

#
# Similar to all_probes, building this dynamically.
# Typically, values are prefixed with a magic character
# (€ for EPCIS PVs, $ for shell env vars, ...). Data which
# doesn't have any prefix is used verbatim, as constants).
#
all_values = {
    v.pref:v for k,v in globals().items() \
    if (inspect.isclass(v) and \
        issubclass(v, _value_probe) and \
        (v not in (_value_probe,)))
}


def make_probe(args):
    '''
    Builds a probe from an arguments iterator.
    '''
    return consume_probe(args.copy())


def consume_probe(args, context=None, greed_rank=None):
    '''
    Recursively builds a probe expression from an arguments list.
    Modifies the list to jump past the probe.

    This is a low-level function, don't use it. Use `make_probe()`
    instead.

    Args:
        args: list of strings, one Value or Operator each.
        context: if specified, it's an l-value (context) for binary
          operators.
        greed_rank: if specified, it's the rank of the operator
          that produced `context`. Used to determine operator
          precedence.

    Returns: the top-level probe (i.e. the one that evaluates to
    all the expressions in `args`.
    '''

    # DON'T TOUCH THIS.

    # NO, really. DON'T.

    # If you think you have to, here's some useful info.
    # Operator priority generally works like this:
    #
    # Operator ranking (i.e. higher precedence):
    #  - 10: unary modifyer (- a.k.a. INV)
    #  -  8: binary comparison (==, !=, <, >, <=, >=)
    #  -  6: unary boolean (! a.k.a. NOT)
    #  -  4: binary boolean && (a.k.a. AND)
    #  -  2: binary boolean || (a.k.a. OR)
    #
    # The idea now is that we walk the "args" list and try to evaluate
    # each operator we encounter. At any point for any operator there's
    # always the _next_ item that it operates on (rval), and the _previous_
    # one (i.e. lval, we call it "context", possibly `None`) item that can
    # be used.
    #
    # We act like this is true for unary and binary operators likewise,
    # it's only that unary operators simply don't care for
    # the previous item (i.e. tose act only on the rval, regardless
    # of the value or existence of an lval).
    #
    # Precedence is a question of where we delimit the "next item":
    #
    #  - if the current operator is lower ranked than the one that
    #    comes after it, we need to be "greedy", i.e. proceed to
    #    evaluating that first before we return a value.
    #    Example: ... || 2 == ...    
    #
    #  - if the current operator is higher-or-equal-ranked, we need
    #    to return the value without sub-processing following operators.
    #    Example: ... == 2 && ...    
    #
    # As such, we have a `greed_rank` parameter that we pass on
    # recursively, as we look for the value (rval) to operate on.

    if len(args) == 0:
        # This is typically the exit point; eventually we always land
        # here by the end of the evaluation recursion. The actual result
        # is then our lvalue context.
        return context

    class NotAnOperator(Exception): pass
    
    a = args[0]
    
    try:
        Op = all_probes.get(a, None)
        if Op is None:
            raise NotAnOperator()

        # This is an operator.
        #
        # Any way we look at it, the element in args[] is the one this
        # operator applies to; i.e. this operator's rval.
        #
        # If we already have a `context`, that's our lval.
        #
        # `greed_rank` indicates how we have to compute rval:
        #
        #   - If previous operation's rank (i.e. the one that produced the
        #     `context` value) is higher than our own, then we're
        #     breaking the evaluation link
        #
        # If current operation has lower rank than previous one
        # (which generated the data in `context`), then we're at
        # the end of recursion and we need  Op(context, value)
        # as one final result.
        
        prev_rank = greed_rank if greed_rank is not None else 0

        if prev_rank < Op.rank:
            # This is the case if prev-rank is lower: this operator
            # evaluates to Op([context,] rval)
            del args[0]
            lval = context
            rval = consume_probe(args, context=None, greed_rank=Op.rank)
            if issubclass(Op, _unary_probe):
                this = Op(rval)
            elif issubclass(Op, _binary_probe):
                this = Op(l=context, r=rval)
            else:
                raise RuntimeError(f'near={a} msg="Expected operator"')

            # Continue processing to the rest of `args`, use the result so far
            # (stored in `this`) as lval context.
            return consume_probe(args, context=this, greed_rank=None)

        else:
            # This is the case of prev-rank is same or higher: this operator
            # evalueates to its lval.
            return context


    except NotAnOperator:
        
        # This is a value; whether we return the value as-is, or start
        # evaluating the arguments chain, depends on whether the operator
        # _after_ this value (consume_probe()) is stronger than the one
        # before (`greed_rank`).
        #
        # This is a decision we can't meet here, we need to defer to sub-calls
        # of consume_probe(), because we don't know future ranks -- only
        # the current and the previous (?)
        
        Val = all_values.get(a[0], all_values[None])
        del args[0]
        
        if greed_rank is None:
            # This is an l-value; we start anew at the lowest rank.
            # We pass our own value as context.
            return consume_probe(args, context=Val(a), greed_rank=Val.rank)
        else:
            # This is an r-value, we've inherited the OP rank in `greed_rank`.
            # (Why are we passing a context?)
            # Example ... _ ==  2  && _ ...   vs.   ... ||  2  == ...
            #                  ^^^                         ^^^
            # This is what it's about, vs               
            # This is where rank should play a role:
            #   - if prev-rank is same or higher, this should be a plain value "2"
            #     (eval stops there?)
            #   - if prev-rank is lower, the rest of _args_ need to be evaluated
            #     together with "2"
            return consume_probe(args, context=Val(a), greed_rank=greed_rank)

    raise RuntimeError(f'You\'re not supposed to be here with "{args}"')
