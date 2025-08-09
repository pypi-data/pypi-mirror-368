from collections.abc import Callable
import typing
import types

_CopiableMappings = dict[str, typing.Any] | types.MappingProxyType[str, typing.Any]

def get_func_annotations(
    func: types.FunctionType,
) -> dict[str, typing.Any]: ...

def get_ns_annotations(
    ns: _CopiableMappings,
) -> dict[str, typing.Any]: ...

def make_annotate_func(
    annos: dict[str, typing.Any]
) -> Callable[[int], dict[str, typing.Any]]: ...

def is_classvar(
    hint: object,
) -> bool: ...
