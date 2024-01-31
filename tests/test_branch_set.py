import pytest

from nzshm_model.branch_prop import get_branch_set


def test_get_branch_set():
    assert len(list(get_branch_set('NSHM_v1.0.4', 'CRU').branches)) == 36


def test_get_branch_set_invalid_model_version():
    with pytest.raises(ValueError):
        get_branch_set('', 'CRU')


def test_get_branch_set_invalid_branch():
    with pytest.raises(ValueError):
        get_branch_set('NSHM_v1.0.4', 'AAA')
