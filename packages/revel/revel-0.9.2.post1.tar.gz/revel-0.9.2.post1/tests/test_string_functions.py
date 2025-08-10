from typing import *  # type: ignore

import pytest

import revel


@pytest.mark.parametrize(
    "options, input, expected",
    [
        (["Foo Bar", "Bar Baz", "Eggs", "Spam"], "Foo Bar", 0),
        (["Foo Bar", "Bar Baz", "Eggs", "Spam"], "Foo", 0),
        (["Foo Bar", "Bar Baz", "Eggs", "Spam"], "fo", 0),
        (["Foo Bar", "Bar Baz", "Eggs", "Spam"], "bar", revel.AmbiguousOptionError),
        (["Foo Bar", "Bar Baz", "Eggs", "Spam"], "baz", 1),
        (["Foo Bar", "Bar Baz", "Eggs", "Spam"], "gg", 2),
        (["Foo Bar", "Bar Baz", "Eggs", "Spam"], "invalid", revel.NoSuchOptionError),
        ([["a", "b", "match"], ["c", "d"], "e"], "match", 0),
        ([["a", "b", "c"], ["d", "e"], "match"], "match", 2),
    ],
)
def test_choose_string(
    options: list[str | list[str]],
    input: str,
    expected: int | Type[Exception],
) -> None:
    """
    Ensures that `revel.choose_string` selects the correct value in a multitude of scenarios.
    """

    # Case: An option should be chosen
    if isinstance(expected, int):
        chosen_index = revel.choose_string(options, input)
        assert chosen_index == expected

    # Case: An exception should be raised
    else:
        with pytest.raises(expected):
            revel.choose_string(options, input)
