import pytest

import nzshm_model
from nzshm_model.branch_prop import get_source_branch_sets, get_source_branches

# def test_get_source_branch_sets():
#  assert len(list(get_source_branch_sets('NSHM_v1.0.4', 'CRU').branches)) == 36

# def test_get_source_branch_sets_invalid_model_version():
#     with pytest.raises(ValueError):
#         get_source_branch_sets('', 'CRU')


# def test_get_source_branch_sets_invalid_branch():
#     with pytest.raises(ValueError):
#         get_source_branch_sets('NSHM_v1.0.4', 'AAA')


def test_get_source_branch_sets_with_list():
    branch_sets = list(get_source_branch_sets('NSHM_v1.0.4', ['CRU', 'PUY']))
    assert len(branch_sets) == 2
    assert branch_sets[0].short_name == 'PUY'
    assert branch_sets[1].short_name == 'CRU'

    # assert len(get_source_branch_sets('NSHM_v1.0.4', ['CRU'])) == 1


def test_get_source_branch_sets_with_single():
    branch_sets = list(get_source_branch_sets('NSHM_v1.0.4', 'CRU'))
    assert len(branch_sets) == 1
    assert branch_sets[0].short_name == 'CRU'


def test_get_source_branch_sets_with_null():
    assert len(list(get_source_branch_sets('NSHM_v1.0.4', []))) == 4
    assert len(list(get_source_branch_sets('NSHM_v1.0.4'))) == 4


def test_get_source_branch_sets_invalid_model_version():
    with pytest.raises(ValueError, match=r'.* is not a valid') as exc:
        next(get_source_branch_sets('', ['CRU', 'PUY']))

def test_get_source_branch_sets_with_invalid_branch():
    with pytest.raises(StopIteration):
        next(get_source_branch_sets('NSHM_v1.0.4', ['XXX']))



class TestGetBranches():

    def test_get_all_crustal_branches(self):
        cru_branches = next(get_source_branch_sets('NSHM_v1.0.4', 'CRU')).branches
        assert next(get_source_branches('NSHM_v1.0.4', 'CRU')) == cru_branches[0]

    def test_get_source_branches_invalid_model_version(self):
        with pytest.raises(ValueError, match=r'.* is not a valid') as exc:
            next(get_source_branches('', ['CRU', 'PUY']))

    def test_get_source_branches_with_invalid_branch(self):
        with pytest.raises(StopIteration):
            next(get_source_branches('NSHM_v1.0.4', ['XXX']))