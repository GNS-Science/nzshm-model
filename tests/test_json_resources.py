from pathlib import Path

import pytest

from nzshm_model import all_model_versions, get_model_version
from nzshm_model.logic_tree import GMCMLogicTree, SourceLogicTree


@pytest.fixture(scope='module')
def branchset_names():
    return {
        'Active Shallow Crust': {'short_name': 'CRU', 'long_name': 'Crustal'},
        'Subduction Interface': {'short_name': 'INTER', 'long_name': 'Subduction Interface'},
        'Subduction Intraslab': {'short_name': 'SLAB', 'long_name': 'Subduction Intraslab'},
    }


source_json_files = ["nshm_v1.0.0_v2.json", "nshm_v1.0.4_v2.json"]


@pytest.mark.parametrize("model_version, json_filename", zip(all_model_versions(), source_json_files))
def test_json_source(model_version, json_filename):
    model = get_model_version(model_version)
    json_filepath = Path(__file__).parent / 'fixtures' / 'model_versions' / json_filename
    slt_expected = SourceLogicTree.from_json(json_filepath)
    slt_from_model = model.source_logic_tree
    assert slt_from_model == slt_expected


gmcm_json_files = ["gmcm_nshm_v1.0.0.json", "gmcm_nshm_v1.0.4.json"]


@pytest.mark.parametrize("model_version, json_filename", zip(all_model_versions(), gmcm_json_files))
def test_json_gmcm(model_version, json_filename):
    model = get_model_version(model_version)
    json_filepath = Path(__file__).parent / 'fixtures' / 'model_versions' / json_filename
    gmcm_expected = GMCMLogicTree.from_json(json_filepath)
    gmcm_from_model = model.gmm_logic_tree
    assert gmcm_from_model == gmcm_expected


@pytest.mark.parametrize("model_version", all_model_versions())
def test_brachset_names(model_version, branchset_names):
    model = get_model_version(model_version)
    gmcm = model.gmm_logic_tree
    for branch_set in gmcm.branch_sets:
        assert branch_set.short_name == branchset_names[branch_set.tectonic_region_type]['short_name']
        assert branch_set.long_name == branchset_names[branch_set.tectonic_region_type]['long_name']
