from typing import *  # type: ignore

import pytest

import revel.argument_parser as aparse


def _test_assignment(
    raw_args: list[str],
    func: Callable,
    expected: dict[str, Any],
) -> None:
    """
    Assign `raw_args` to the function's parameters and check that the result
    matches `expected`.
    """

    # Create a parser
    parameters = list(p[1] for p in aparse.parameters_from_function(func))
    parser = aparse.Parser(parameters)

    # Assign the arguments
    parser.feed_many(raw_args)
    assignments = parser.finish()

    # Any errors?
    assert parser.errors == []

    # Check the result
    params_by_name = {param.name: param for param in parameters}

    for name, value_should in expected.items():
        param = params_by_name[name]
        value_is = assignments[param]

        assert value_is == value_should


def _test_parsing(
    raw_value: str,
    type: Type,
    expected: Any,
    *,
    should_succeed: bool,
) -> None:
    # Create a parser
    parameters = [
        aparse.Parameter(
            name="a",
            shorthand=None,
            python_name="a",
            prompt=None,
            type=type,
            is_flag=False,
            is_variadic=False,
            default_value=aparse.NO_DEFAULT,
        )
    ]

    parser = aparse.Parser(parameters)

    # Assign the arguments
    parser.feed_one(raw_value)
    assignments = parser.finish()

    # Any errors?
    if should_succeed:
        assert parser.errors == []
    else:
        assert parser.errors != []
        return

    # Check the result
    assert len(assignments) == 1, assignments
    parsed_value = next(iter(assignments.values()))
    assert parsed_value == expected


@pytest.mark.parametrize(
    "raw_value, as_type, result_should",
    (
        # bool
        ("true", bool, True),
        ("yes", bool, True),
        ("y", bool, True),
        ("1", bool, True),
        ("false", bool, False),
        # int
        ("1", int, 1),
        ("-2", int, -2),
        # float
        ("1.2", float, 1.2),
        ("-2.3", float, -2.3),
        # str
        ("hello", str, "hello"),
        # Literal
        ("hello", Literal["hello"], "hello"),
        ("hello", Literal["hello2"], "hello2"),
        ("hello", Literal["hello", "hello2"], "hello"),
    ),
)
def test_parse_valid(raw_value: str, as_type: Type, result_should: Any) -> None:
    _test_parsing(
        raw_value,
        as_type,
        result_should,
        should_succeed=True,
    )


@pytest.mark.parametrize(
    "raw_value, as_type",
    (
        # bool
        ("hello", bool),
        ("2", bool),
        # int
        ("hello", int),
        ("1.2", int),
        # float
        ("hello", float),
        ("1.2.3", float),
        # Literal
        ("hell", Literal["hello", "hello2"]),
    ),
)
def test_parse_invalid(raw_value: str, as_type: Type) -> None:
    _test_parsing(
        raw_value,
        as_type,
        "<should not be reached>",
        should_succeed=False,
    )


def test_empty():
    def func():
        pass

    _test_assignment(
        [],
        func,
        {},
    )


def test_single_positional():
    def func(a: str):
        pass

    _test_assignment(
        ["A"],
        func,
        {"a": "A"},
    )


def test_single_positional_only():
    def func(a: str, /):
        pass

    _test_assignment(
        ["A"],
        func,
        {"a": "A"},
    )


def test_single_keyword_only():
    def func(*, a: str):
        pass

    _test_assignment(
        ["--a=A"],
        func,
        {"a": "A"},
    )


def test_multiple():
    def func(a: str, b: str):
        pass

    _test_assignment(
        ["--b=B", "A"],
        func,
        {"a": "A", "b": "B"},
    )
