import configparser
import importlib.resources as resources

import pytest

import nzshm_model as nm
from nzshm_model.model import NshmModel
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
        with pytest.raises(ValueError):
            list(current_model.get_source_branch_sets(['XXX']))

    def test_unknown_short_name_raises_value_error(self, current_model):
        """get_source_branch_sets must raise ValueError when a short_name is not found."""
        with pytest.raises(ValueError, match="XXX"):
            list(current_model.get_source_branch_sets(['XXX']))


class TestFromFilesWithV1Slt:
    def test_v1_slt_json_loads_correctly(self):
        """from_files must use the v1 migration path when logic_tree_version is absent.

        Regression for: the missing else: caused SourceLogicTree.from_json to be called
        unconditionally, which fails on v1-format SLT files.
        """
        rpath = resources.files('nzshm_model.resources')
        v1_slt_json = rpath / 'SRM_JSON' / 'nshm_v1.0.4.json'
        gmm_json = rpath / 'GMM_JSON' / 'gmcm_nshm_v1.0.4.json'
        haz_json = rpath / 'HAZARD_CONFIG_JSON' / 'oq_config_nshm_v1.0.4.json'

        model = NshmModel.from_files(
            version='NSHM_v1.0.4',
            title='test v1 migration',
            slt_json=str(v1_slt_json),
            gmm_json=str(gmm_json),
            hazard_config_json=str(haz_json),
        )
        assert len(model.source_logic_tree.branch_sets) == 4


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
