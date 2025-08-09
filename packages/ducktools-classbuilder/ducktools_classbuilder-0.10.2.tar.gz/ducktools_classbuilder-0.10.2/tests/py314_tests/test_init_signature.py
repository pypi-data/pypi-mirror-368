from annotationlib import get_annotations, Format

import pytest


from ducktools.classbuilder.prefab import Prefab, prefab
from _test_support import EqualToForwardRef


# Aliases for alias test
assign_int = int
type type_str = str


@pytest.mark.parametrize(
    ["format", "expected"],
    [
        (Format.VALUE, {"return": None, "x": str, "y": int}),
        (Format.FORWARDREF, {"return": None, "x": str, "y": int}),
        (Format.STRING, {"return": "None", "x": "str", "y": "int"}),
    ]
)
def test_resolvable_annotations(format, expected):
    @prefab
    class Example:
        x: str
        y: int

    annos = get_annotations(Example.__init__, format=format)

    assert annos == expected

    class Example(Prefab):
        x: str
        y: int

    annos = get_annotations(Example.__init__, format=format)

    assert annos == expected


@pytest.mark.parametrize(
    ["format", "expected"],
    [
        (Format.VALUE, {"return": None, "x": str, "y": int}),
        (Format.FORWARDREF, {"return": None, "x": str, "y": int}),
        (Format.STRING, {"return": "None", "x": "str", "y": "late_definition"}),
    ]
)
def test_late_defined_annotations(format, expected):
    # Test where the annotation is a forwardref at processing time
    @prefab
    class Example:
        x: str
        y: late_definition

    late_definition = int

    annos = get_annotations(Example.__init__, format=format)

    assert annos == expected


@pytest.mark.parametrize(
    ["format", "expected"],
    [
        (Format.VALUE, {"return": None, "x": int, "y": type_str}),
        (Format.FORWARDREF, {"return": None, "x": int, "y": type_str}),
        (Format.STRING, {"return": "None", "x": "int", "y": "type_str"}),
    ]
)
def test_alias_defined_annotations(format, expected):
    # Test the behaviour of type aliases and regular types
    # Type Alias names should be kept while regular assignments will be lost

    @prefab
    class Example:
        x: assign_int  # type: ignore
        y: type_str

    annos = get_annotations(Example.__init__, format=format)

    assert annos == expected


@pytest.mark.parametrize(
    ["format", "expected"],
    [
        (Format.FORWARDREF, {"return": None, "x": str, "y": EqualToForwardRef("undefined")}),
        (Format.STRING, {"return": "None", "x": "str", "y": "undefined"}),
    ]
)
def test_forwardref_annotation(format, expected):
    # Test where the annotation is a forwardref at processing and analysis
    class Example(Prefab):
        x: str
        y: undefined

    annos = get_annotations(Example.__init__, format=format)

    assert annos == expected


def test_forwardref_raises():
    # Should still raise a NameError with VALUE annotations
    @prefab
    class Example:
        x: str
        y: undefined

    with pytest.raises(NameError):
        annos = get_annotations(Example.__init__, format=Format.VALUE)


def test_raises_with_fake_globals():
    @prefab
    class Example:
        x: str
        y: undefined

    with pytest.raises(NotImplementedError):
        annos = Example.__init__.__annotate__(Format.VALUE_WITH_FAKE_GLOBALS)
