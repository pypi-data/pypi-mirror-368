__all__ = [
    "Directive",
    "get_directive_plugin",
    "is_directive",
    "load_directive_plugins",
    "unravel_directive",
]

import re
from dataclasses import dataclass
from importlib.metadata import EntryPoint
from importlib.metadata import entry_points
from typing import Callable

DIRECTIVE_PATTERN = re.compile(r"^([a-zA-Z]\w+)/{2}(.*)$")


@dataclass
class Directive:
    ep: EntryPoint

    @property
    def name(self) -> str:
        return self.ep.name

    @property
    def func(self) -> Callable:
        return self.ep.load()


# Keep a record of all navdict directive plugins
_directive_plugins: dict[str, Directive] = {}


def load_directive_plugins():
    """
    Load any navdict directive plugins that are available in your environment.
    """
    global _directive_plugins

    eps = entry_points()
    print(sorted(eps.groups))
    eps = eps.select(group="navdict.directive")

    for ep in eps:
        _directive_plugins[ep.name] = Directive(ep=ep)


def is_directive(value: str) -> bool:
    """Returns True if the value matches a directive pattern, i.e. 'name//value'."""
    if isinstance(value, str):
        match = re.match(DIRECTIVE_PATTERN, value)
        return match is not None
    else:
        return False


def unravel_directive(value: str) -> tuple[str, str]:
    """
    Returns the directive key and the directive value in a tuple.

    Raises:
        A ValueError if the given value is not a directive.
    """
    match = re.match(DIRECTIVE_PATTERN, value)
    if match:
        return match[1], match[2]
    else:
        raise ValueError(f"Value is not a directive: {value}")


def get_directive_plugin(name: str) -> Directive | None:
    """Returns the directive that matches the given name or None if no plugin was loaded with that name."""
    return _directive_plugins.get(name)


# Load all directive plugins during import
load_directive_plugins()
