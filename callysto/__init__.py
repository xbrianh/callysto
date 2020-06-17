import io
import os
import json
import typing


class Object:
    types = ["PYTHON", "MARKDOWN"]
    actions = dict(PYTHON=["CELL", "TEST", "INJECT"],
                   MARKDOWN=["CELL"])

    _translate = dict(PYTHON="code", MARKDOWN="markdown")

    def __init__(self, lines):
        obj_type, action = lines[0].split()[1:]
        assert obj_type in self.types
        assert action in self.actions[obj_type]
        self.type = obj_type
        self.action = action
        self.lines = lines[1:]

    def to_ipynb_cell(self):
        if "CELL" == self.action:
            return dict(cell_type=self._translate[self.type],
                        execution_count=None,
                        metadata=dict(),
                        outputs=list(),
                        source=os.linesep.join(self.lines))
        else:
            raise ValueError(f"Cannot convert {self.action} object to a Jupyter cell")

    def is_cell(self):
        return "CELL" == self.action

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
            if line.startswith("@CALLYSTO"):
                break
        obj = [line]
        for line in self.lines():
            if line.startswith("@CALLYSTO"):
                yield Object(obj)
                obj = [line]
            else:
                obj.append(line)
        if obj:
            yield Object(obj)

def evaluate(handle: io.FileIO):
    p = Parser(handle)
    global_vars: typing.Dict[typing.Any, typing.Any] = dict()
    local_vars: typing.Dict[typing.Any, typing.Any] = dict()
    for obj in p.objects:
        if "PYTHON" == obj.type and "CELL" == obj.action:
            if obj.action in ["CELL", "INJECT"]:
                code = os.linesep.join(obj.lines)
                exec(code, global_vars, local_vars)
            elif "TEST" == obj.action:
                test_globals = global_vars.copy()
                test_locals = local_vars.copy()
                code = os.linesep.join(obj.lines)
                exec(code, test_globals, test_locals)

def generate(handle: io.FileIO):
    p = Parser(handle)
    cells = [obj.to_ipynb_cell() for obj in p.objects
             if obj.is_cell()]
    with open(os.path.join(os.path.dirname(__file__), "data", "python_3_boiler.json")) as fh:
        boiler = json.loads(fh.read())
    ipynb = dict(cells=cells, **boiler)
    return ipynb
