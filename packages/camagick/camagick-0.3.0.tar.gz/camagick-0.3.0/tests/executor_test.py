import pytest, asyncio, pprint

from camagick.executor import *

from camagick import source, sink

from schema import SchemaError, SchemaUnexpectedTypeError, Optional

@pytest.fixture
def example_args():
    return (
        '--from-epics', 'prefix=KE:threshold_1:', 'image=image', 'guide=KE:acquire==0', 'width=asize1', 'height=asize2',
        '--reshape', 'shape=1,512,1028',
        '{',
        
          '--to-tiff', 'pathfmt=/home/specuser/data/image-{seq}.tif',
        
          '[',
        
            '{',
              '[',
                '--slice', '0', '10:490', '520:550',
                '{',
                  '--npfun', 'max',
                  '--npfun', 'sum',
                '}',
              ']',
              '--npfun', 'sum',
              '--npfun', 'max',
              '--npfun', 'min',
            '}',
        
            '{',
              '--to-ioc',
              '--to-summary',
            '}',
        
          ']',
        
        '}'
    )

@pytest.fixture
def example_spec2():

    return {
        "chain": [{"from": "epics",
                   "params": {
                       "image": "KE:threshold_1:image",
                       "guide": "KE:acquire==0",
                       "width": "KE:threshold_1:asize1",
                       "height": "KE:threshold_1:asize2",}},

                  {"via": [ "demote", "width", "height" ] },
                  
                  {"via": "reshape",
                   "params": {"shape": [1, 512, 1028]}},
                  
                  {"fanout": [{"to": "tiff",
                               "params": { "pathfmt": "/home/specuser/data/image-{seq}.tif"} },

                              {"chain": [{"fanout": [{"chain": [{"via": [ "slice", "0,10:490,520:550"  ],},
                                                                {"fanout": [{"via": "npfun", "params": { "op": "max" },},
                                                                            {"via": "npfun", "params": { "op": "sum" },},],}, ], },

                                                     {"via": [ "npfun", "sum" ], },

                                                     {"via": "npfun", "params": { "op": "max" },},

                                                     {"via": "npfun", "params": { "op": "min" },},], },

                                         {"fanout": [{"to": "ioc"},
                                                     {"to": "summary"},], },], }, ], }, ],
    }


def test_sequence():
    print(Sequence(int, float).validate([23, 2.4]))

    with pytest.raises(SchemaSequenceTooShortError):
        print(Sequence(int, float).validate([23]))

    with pytest.raises(SchemaUnexpectedTypeError):
        print(Sequence(int, float).validate([2.4]))

    with pytest.raises(SchemaUnexpectedTypeError):
        print(Sequence(int, float).validate([2.3, 24]))

    with pytest.raises(SchemaSequenceTooLongError):
        print(Sequence(int, float).validate([23, 3.14, 1]))

    print(Sequence(int, float, Optional(int)).validate([23, 3.14]))

    print(Sequence(int, float, Sequence.VarArguments([object]))\
          .validate([12, 3.4, "moo", 6, True]))


def test_mktype():
    assert make_pipe_type("source", "ioc") == source.ioc.Processor
    assert make_pipe_type("source", "camagick.source.ioc") == source.ioc.Processor
    assert make_pipe_type("source", "camagick.source.ioc:Processor") == source.ioc.Processor

    # "kind" not important when using dotted notation
    assert make_pipe_type(None, "camagick.source.ioc") == source.ioc.Processor


def test_validator():
    PipeValidator()


def test_with_pipe(example_spec2):
    
    print()
    with_pipe([example_spec2], print)

    pm = PipeMaker()

    with_pipe([example_spec2], pm)

    print('Stack:', pm)
    

def test_validate(example_spec2):

    scm = PipeValidator()

    r1 = scm.validate({
        "chain": [
            { "from": [ "epics", "moo" ] },
            { "via": "npfun", "params": { "op": "sum" } },
            { "via": "npfun", "params": [ "sum" ] },
            { "via": [ "npfun", "sum" ] },
            { "via": [ "demote", "moo" ] },
            { "to": "summary" },
        ]
    })

    assert len(r1) > 0

    r2 = scm.validate({
        "fanout": [
            { "from": "ioc", "params": { "prefix": "fum" } },
            { "chain": [
                { "via": "npfun", "params": [ "sum" ] },
                { "to": "summary" },],},
            { "to": "ioc" },
        ]        
    })

    assert len(r2) > 0

    r3 = scm.validate(example_spec2)


def test_args(example_args):
    spec = pipe_spec_from_args(example_args)

    pprint.pprint(spec)
