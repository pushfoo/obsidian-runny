import pytest
from obsidian_runny.mappings.iteration import iter_as_pairs


@pytest.fixture(params=[
    iter,
    tuple,
    list
])
def iter_type(request):
    return request.param


@pytest.fixture(params=[
    (("tooshort",)),
    ("toolong",)
])
def bad_pair_length(request, iter_type):
    return iter_type(request.param)


def test_throws_type_error_on_non_iterables():
    with pytest.raises(TypeError):
        for _, _ in iter_as_pairs(1):  # type: ignore
            pass


def test_throws_value_error_on_bad_pair_lengths(bad_pair_length):
    with pytest.raises(ValueError):
        for _, _ in iter_as_pairs(bad_pair_length):
            pass


def test_handles_well_formed_dict():
    d = dict(
        a=1,
        b=2
    )
    for k, v in iter_as_pairs(d):
        assert d[k] is v


def test_handles_well_formed_pairs():
    pairs = [
        ('a', 1),
        ('b', 2)
    ]

    for original_pair, it_pair in zip(pairs, iter_as_pairs(pairs)):
        assert original_pair[0] is it_pair[0]
        assert original_pair[1] is it_pair[1]

