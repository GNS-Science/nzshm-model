import configparser

import pytest

import nzshm_model as nm
from nzshm_model.psha_adapter.openquake.hazard_config_compat import DEFAULT_HAZARD_CONFIG


def test_list_all_models(current_version):
    assert current_version in nm.all_model_versions()


def test_mutable_model(current_version):
    model = nm.get_model_version(current_version)
    slt = model.source_logic_tree
    slt.branch_sets = [bs for bs in slt.branch_sets if bs.short_name == "CRU"]
    model.source_logic_tree.branch_sets = [bs for bs in model.source_logic_tree.branch_sets if bs.short_name == "CRU"]
    assert len(model.source_logic_tree.branch_sets) == len(slt.branch_sets)


class TestLoadModel:
    def test_load_model_104(self, current_version):
        model = nm.model.NshmModel.get_model_version(current_version)
        assert model

    def test_model_104_title(self, current_model):
        assert current_model.title == "NSHM version 1.0.4, corrected fault geometry"


class TestGetSourceBranchSets:
    def test_with_list(self, current_model):
        branch_sets = list(current_model.get_source_branch_sets(['CRU', 'PUY']))
        assert len(branch_sets) == 2
        assert branch_sets[0].short_name == 'CRU'
        assert branch_sets[1].short_name == 'PUY'

    def test_with_single(self, current_model):
        branch_sets = list(current_model.get_source_branch_sets('CRU'))
        assert len(branch_sets) == 1
        assert branch_sets[0].short_name == 'CRU'

    def test_with_null(self, current_model):
        assert len(list(current_model.get_source_branch_sets([]))) == 4
        assert len(list(current_model.get_source_branch_sets())) == 4

    def test_with_invalid_branch(self, current_model):
        with pytest.raises(StopIteration):
            next(current_model.get_source_branch_sets(['XXX']))


class TestConfig:
    def test_openquake_config(self, current_model):
        expected = configparser.ConfigParser()
        expected.read_dict(DEFAULT_HAZARD_CONFIG)
        assert current_model.hazard_config.config == expected


class TestGetNewModel:
    def test_get_new_model(self, current_version):
        new_model_title = "NEW MODEL TITLE"
        model1 = nm.get_model_version(current_version)
        model1.title = new_model_title

        model2 = nm.get_model_version(current_version)
        assert model1.title == new_model_title
        assert model2.title != new_model_title


# class TestGetSourceBranches:
#     def test_get_first_crustal_branch(self, model_104):
#         cru_branches = next(model_104.get_source_branch_sets('CRU')).branches
#         assert next(model_104.get_source_branches('CRU')) == cru_branches[0]

#     def test_invalid_branch_set(self, model_104):
#         with pytest.raises(StopIteration):
#             next(model_104.get_source_branches(['XXX']))
