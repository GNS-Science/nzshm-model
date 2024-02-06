import pytest

from nzshm_model.branch_prop import get_branch_set

# def test_get_branch_set():
#     assert len(list(get_branch_set('NSHM_v1.0.4', 'CRU').branches)) == 36


# def test_get_branch_set_invalid_model_version():
#     with pytest.raises(ValueError):
#         get_branch_set('', 'CRU')


# def test_get_branch_set_invalid_branch():
#     with pytest.raises(ValueError):
#         get_branch_set('NSHM_v1.0.4', 'AAA')


def test_get_branch_set_with_list():
    assert len(get_branch_set('NSHM_v1.0.4', ['CRU', 'PUY'])) == 2
    assert get_branch_set('NSHM_v1.0.4', ['CRU', 'PUY'])[0].short_name == 'CRU'
    assert get_branch_set('NSHM_v1.0.4', ['CRU', 'PUY'])[1].short_name == 'PUY'
    assert len(get_branch_set('NSHM_v1.0.4', ['CRU'])) == 1


def test_get_branch_set_with_single():
    assert len(get_branch_set('NSHM_v1.0.4', 'CRU')) == 1
    assert get_branch_set('NSHM_v1.0.4', 'CRU')[0].short_name == 'CRU'


def test_get_branch_set_with_null():
    assert len(get_branch_set('NSHM_v1.0.4', [])) == 4
    assert len(get_branch_set('NSHM_v1.0.4')) == 4


def test_get_branch_set_invalid_model_version():
    with pytest.raises(ValueError):
        get_branch_set('', ['CRU', 'PUY'])


def test_get_branch_set_invalid_branch():
    with pytest.raises(ValueError):
        get_branch_set('NSHM_v1.0.4', ['XXX'])
        get_branch_set('NSHM_v1.0.4', 'XXX')
