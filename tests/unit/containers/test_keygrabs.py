import pytest

from obsidian_runny.mappings.iteration import (
    # per_key,
    pop_item,
    # get_keys,
    # pop_keys,
)


@pytest.fixture(params=(pop_item,))
def key_helper_fn(request):
    return request.param

METHOD_NAME_LUT = {
    pop_item: "pop"
}


@pytest.fixture
def wrapped_helper_fn(key_helper_fn):
    return METHOD_NAME_LUT[key_helper_fn]


def test_pop_item_pops_value(key_helper_fn):
    d = dict(a=1)
    assert key_helper_fn(d, "a") == 1


def test_pop_item_key_error_on_missing():
    with pytest.raises(KeyError):
        pop_item({}, "a")

# Further tests pending review (i.e. "Is this idea silly?" / YAGNI)
#
# @pytest.fixture(params=(
#     dict,
#     lambda d: d.items()
# ))
# def type_fn_dictargslike(request) -> Callable[[Mapping[K, V]], DictArgsLike[K,V]]:
#     return request.param  # type: ignore
#
# def test_per_key():
#     def do_not_touch_map(_, k):
#         return None
#     dict_mock = MagicMock(spec=dict)

