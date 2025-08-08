import pytest
from good_common.utilities import (
    try_chain,
    deep_attribute_get,
    deep_attribute_set,
    set_defaults,
    filter_nulls,
)


# Test for try_chain
def test_try_chain():
    def fail_func():
        raise ValueError("Failed")

    def success_func(x):
        return x * 2

    chain = try_chain([fail_func, success_func])
    assert chain(5) == 10

    fail_chain = try_chain([fail_func, fail_func], fail=True)
    with pytest.raises(ValueError):
        fail_chain(5)

    default_chain = try_chain([fail_func, fail_func], default_value="default")
    assert default_chain(5) == "default"


# Tests for deep_attribute_get
def test_deep_attribute_get():
    obj = {
        "a": {"b": [{"c": 1}, {"c": 2}], "d": {"e": "value"}},
        "f": [1, 2, 3],
        "g": {"h": [{"i": "test"}]},
    }

    assert deep_attribute_get(obj, "a.b[0].c") == 1
    # assert deep_attribute_get(obj, "a.b[*].c") == [1, 2] NOT SUPPORTED
    assert deep_attribute_get(obj, "a.d.e") == "value"
    assert deep_attribute_get(obj, "f[1]") == 2
    assert deep_attribute_get(obj, "g.h[0].i") == "test"
    assert deep_attribute_get(obj, "nonexistent", default="not found") == "not found"

    result = deep_attribute_get(obj, "a.b[*].c", return_paths=True)
    assert result == [(1, "a.b[0].c"), (2, "a.b[1].c")]


# Test for deep_attribute_set
def test_deep_attribute_set():
    obj = {"a": {"b": {"c": 1}}}
    deep_attribute_set(obj, "a.b.c", 2)
    assert obj["a"]["b"]["c"] == 2

    deep_attribute_set(obj, "a.b.d", 3)
    assert obj["a"]["b"]["d"] == 3

    # deep_attribute_set(obj, "x.y.z", 4) NOT SUPPORTED
    # assert obj["x"]["y"]["z"] == 4


# Test for set_defaults
# def test_set_defaults():
#     base = {"a": 1, "b": None}
#     result = set_defaults(base, b=2, c=3)
#     assert result == {"a": 1, "b": 2, "c": 3}

#     result = set_defaults(b=2, c=3)
#     assert result == {"b": 2, "c": 3}


# Test for filter_nulls
def test_filter_nulls():
    obj = {
        "a": 1,
        "b": None,
        "c": {"d": 2, "e": None, "f": [1, None, 3]},
        "g": [{"h": 4, "i": None}, {"j": None}, {"k": 5}],
    }

    result = filter_nulls(obj)
    assert result == {"a": 1, "c": {"d": 2, "f": [1, 3]}, "g": [{"h": 4}, {"k": 5}]}


# Additional tests for edge cases and specific behaviors


def test_deep_attribute_get_with_nonexistent_path():
    obj = {"a": {"b": 1}}
    assert deep_attribute_get(obj, "a.c.d", default="not found") == "not found"


def test_try_chain_with_mixed_functions():
    def int_func(x):
        return int(x)

    def float_func(x):
        return float(x)

    def str_func(x):
        return str(x)

    chain = try_chain([int_func, float_func, str_func])
    assert chain("10") == 10
    assert chain("10.5") == 10.5
    assert chain("abc") == "abc"


def test_set_defaults_with_falsy_values():
    base = {"a": 0, "b": ""}
    result = set_defaults(base, a=1, b="test", c=False)
    assert result == {"a": 0, "b": "", "c": False}


def test_filter_nulls_with_empty_containers():
    obj = {"a": [], "b": {}, "c": [None], "d": {"e": None}}
    result = filter_nulls(obj)
    assert result == {}
