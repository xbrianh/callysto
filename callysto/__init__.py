import io
import os
import json
import typing
from copy import deepcopy
import __main__
from types import ModuleType


_getarg = """
def getarg(*args, **kwargs):
    return args, kwargs
args, kwargs = getarg({})
"""

def get_args(argstring):
    global_vars = dict()
    local_vars = dict()
    exec(_getarg.format(argstring), global_vars, local_vars)
    args = local_vars['args']
    kwargs = local_vars['kwargs']
    return args, kwargs

class Callysto:
    def __init__(self, language, is_cell=True):
        self.is_cell = is_cell
        self.language = language
        self._state = None
        self._state_modules = None

    def __enter__(self):
        if not self.is_cell:
            self._state = deepcopy({k:v for k,v in __main__.__dict__.items()
                                    if not isinstance(v, ModuleType)})
            self._state_modules = {k:v for k,v in __main__.__dict__.items()
                                   if isinstance(v, ModuleType)}
        return self

    def __exit__(self, *args, **kwargs):
        if self._state:
            __main__.__dict__.update(self._state)
            for key in __main__.__dict__.copy():
                if key not in self._state:
                    del __main__.__dict__[key]
            __main__.__dict__.update(self._state_modules)

class ParserObject:
    types = ["python", "markdown"]
    _translate = dict(python="code", markdown="markdown")

    def __init__(self, lines):
        args, kwargs = get_args(lines[0].split("(", 1)[1].split(")", 1)[0])
        self.type = args[0]
        assert self.type in self.types
        self.is_cell = kwargs.get('is_cell', True)
        self.lines = lines[1:]
        if "markdown" == self.type:
            self.lines = [l for l in self.lines
                          if not '"""' in l]

    def to_ipynb_cell(self):
        assert self.is_cell
        return dict(cell_type=self._translate[self.type],
                    execution_count=None,
                    metadata=dict(),
                    outputs=list(),
                    source=os.linesep.join(self.lines))

class Parser:
    def __init__(self, handle: io.FileIO):
        self.handle = handle
        self._prev_line = None
        self.objects = [c for c in self._parse_objects()]

    def lines(self):
        for line in self.handle:
            yield line

    def _parse_objects(self):
        for line in self.lines():
            if line.startswith("with Callysto"):
                break
        obj = [line]
        for line in self.lines():
            if line.startswith("with Callysto"):
                yield ParserObject(obj)
                obj = [line]
            else:
                obj.append(line[4:].rstrip())
        if obj:
            yield ParserObject(obj)

def generate(handle: io.FileIO):
    p = Parser(handle)
    cells = [obj.to_ipynb_cell() for obj in p.objects
             if obj.is_cell]
    with open(os.path.join(os.path.dirname(__file__), "data", "python_3_boiler.json")) as fh:
        boiler = json.loads(fh.read())
    ipynb = dict(cells=cells, **boiler)
    return ipynb
