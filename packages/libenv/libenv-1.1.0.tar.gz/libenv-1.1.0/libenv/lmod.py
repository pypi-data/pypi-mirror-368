from typing import List, Union, Sequence
from enum import Enum
from pathlib import Path
import os
import re

from .console import expand

lcmd = re.compile(r'([^(]+)\(\s*("([^"]*)")?(,\s*"([^"]*)")*\s*\)\s*$')
"""
>>> m = lcmd.match('ok("a","b")')
>>> m[0]
'ok("a","b")'
>>> m[1]
'ok'
>>> m[2]
'"a"'
>>> m[3]
'a'
>>> m[4]
',"b"'
>>> m[5]
'b'
"""

from .console import read_command

def quote(x: str) -> str:
    """quote - enclose in ""-s
    """
    assert '"' not in x
    assert '\\' not in x
    return f'"{x}"'

class Cmd:
    def __init__(self, cmd: str, *args: str) -> None:
        self.cmd = cmd
        self.args = args
        self.s = f"{cmd}({','.join(self.quoted_args())})"
    @classmethod
    def parse(cls, s: str) -> "Cmd":
        m = lcmd.match(s)
        if m is None:
            raise ValueError(f"Unable to parse command: {s}")
        g = m.groups()
        if len(g) == 1:
            return cls(g[0])
        return cls(g[0], *[x for x in g[2::2] if x is not None])

    def quoted_args(self):
        qargs = []
        for a in self.args:
            try:
                qargs.append( quote(expand(a)) )
            except AssertionError:
                raise ValueError(f"Error - invalid argument string: {a}")
        return qargs
    def __repr__(self) -> str:
        return f"Cmd({','.join(map(repr, (self.cmd,)+self.args))})"
    def __str__(self) -> str:
        return self.s

class Error(Cmd):
    def __init__(self, name: str) -> None:
        Cmd.__init__(self, "LmodError", name)

class Load(Cmd):
    def __init__(self, names: Union[str, List[str]]):
        if isinstance(names, str):
            names = [names]
        else:
            names = names
        Cmd.__init__(self, "load", *names)

class Unload(Cmd):
    def __init__(self, names: Union[str, List[str]]):
        if isinstance(names, str):
            names = [names]
        else:
            names = names
        Cmd.__init__(self, "unload", *names)

class Mode(str,Enum):
    set = "pushenv"
    append = "append_path"
    prepend = "prepend_path"

class SetEnv(Cmd):
    def __init__(self, name: str, val: str, mode=Mode.set):
        Cmd.__init__(self, mode.value, name, val)
class Prepend(SetEnv):
    def __init__(self, name: str, val: str):
        SetEnv.__init__(self, name, val, Mode.prepend)
class Append(SetEnv):
    def __init__(self, name: str, val: str):
        SetEnv.__init__(self, name, val, Mode.append)

class Lmod:
    """ An Lmod script represents a list of Lmod commands.
    """
    def __init__(self, cmds: Sequence[Cmd] = []) -> None:
        self.cmds: List[Cmd] = list(cmds)
    @classmethod
    def parse(cls, s: List[str]) -> "Lmod":
        cmds = [Cmd.parse(line) for line in s]
        return cls(cmds)
    def append(self, cmd: Cmd) -> None:
        self.cmds.append( cmd )
    def extend(self, rhs: "Lmod") -> "Lmod":
        """ In-place update by extending self
            with the commands from the right-hand side.
            This is the monoid addition rule.
        """
        self.cmds += rhs.cmds
        return self
    def __add__(self, rhs: "Lmod") -> "Lmod":
        return Lmod(self.cmds + rhs.cmds)
    def __str__(self) -> str:
        if len(self.cmds) == 0:
            return ""
        return "\n".join( map(str, self.cmds) ) + "\n"
    def __len__(self):
        return len(self.cmds)
    def write(self, path: Path) -> None:
        path.write_text(str(self))

def LmodError(name):
    return Lmod([Error(name)])
