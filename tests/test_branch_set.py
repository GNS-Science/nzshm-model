import pytest

from nzshm_model.branch_prop import get_branch_set


def test_get_branch_set():
    assert len(list(get_branch_set('NSHM_v1.0.4', 'CRU').branches)) == 36

    with pytest.raises(AttributeError):
        get_branch_set('', 'CRU')
    with pytest.raises(StopIteration):
        get_branch_set('NSHM_v1.0.4', 'AAA')
