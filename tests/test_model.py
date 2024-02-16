import pytest

import nzshm_model as nm

CURRENT_MODEL = 'NSHM_v1.0.4'


@pytest.fixture(scope="module")
def model_104():
    # yield nm.model.NshmModel.get_model_version(CURRENT_MODEL)
    yield nm.get_model_version(CURRENT_MODEL)


def test_list_all_models():
    assert CURRENT_MODEL in nm.all_model_versions()


class TestLoadModel:
    def test_load_model_104(self):
        model = nm.model.NshmModel.get_model_version(CURRENT_MODEL)
        assert model

    def test_model_104_title(self, model_104):
        assert model_104.title == "NSHM version 1.0.4, corrected fault geometry"


class TestGetSourceBranchSets:
    def test_with_list(self, model_104):
        branch_sets = list(model_104.get_source_branch_sets(['CRU', 'PUY']))
        assert len(branch_sets) == 2
        assert branch_sets[0].short_name == 'CRU'
        assert branch_sets[1].short_name == 'PUY'

    def test_with_single(self, model_104):
        branch_sets = list(model_104.get_source_branch_sets('CRU'))
        assert len(branch_sets) == 1
        assert branch_sets[0].short_name == 'CRU'

    def test_with_null(self, model_104):
        assert len(list(model_104.get_source_branch_sets([]))) == 4
        assert len(list(model_104.get_source_branch_sets())) == 4

    def test_with_invalid_branch(self, model_104):
        with pytest.raises(StopIteration):
            next(model_104.get_source_branch_sets(['XXX']))


# class TestGetSourceBranches:
#     def test_get_first_crustal_branch(self, model_104):
#         cru_branches = next(model_104.get_source_branch_sets('CRU')).branches
#         assert next(model_104.get_source_branches('CRU')) == cru_branches[0]

#     def test_invalid_branch_set(self, model_104):
#         with pytest.raises(StopIteration):
#             next(model_104.get_source_branches(['XXX']))
