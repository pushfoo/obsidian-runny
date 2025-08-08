import pytest
from obsidian_runny.mappings import ParamDict


@pytest.fixture
def p():
    return ParamDict(dict(a=None, b=1, c=None, d=False, e=True))


def test_init_only_removes_none_keys(p):
    assert len(p) == 3
    assert p['b'] == 1
    assert p['d'] is False
    assert p['e'] is True


def test_init_raises_typeerror_when_both_args_and_kwargs():
    with pytest.raises(TypeError):
        _ = ParamDict([], key=1)


def test_setting_deletes(p):
    p['b'] = None
    assert 'b' not in p
    p['d'] = None
    assert 'd' not in p
    p['e'] = None
    assert 'e' not in p
    assert len(p) == 0


def test_setting_non_none_sets(p):
    p['a'] = False
    assert 'a' in p
    p['c'] = ""
    assert 'c' in p

