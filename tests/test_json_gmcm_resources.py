import pytest

from nzshm_model import all_model_versions, get_model_version


@pytest.fixture(scope='module')
def branchset_names():
    return {
        'Active Shallow Crust': {'short_name': 'CRU', 'long_name': 'Crustal'},
        'Subduction Interface': {'short_name': 'INTER', 'long_name': 'Subduction Interface'},
        'Subduction Intraslab': {'short_name': 'SLAB', 'long_name': 'Subduction Intraslab'},
    }


@pytest.mark.parametrize("model_version", all_model_versions())
def test_json_gmcm(model_version):
    model = get_model_version(model_version)
    gmcm_from_xml = model.gmm_logic_tree_from_xml
    gmcm_from_json = model.gmm_logic_tree

    # the gmcm lt from the xml will not have short_name and long_name
    for branch_set in gmcm_from_json.branch_sets:
        branch_set.short_name = ''
        branch_set.long_name = ''

    assert gmcm_from_json == gmcm_from_xml


@pytest.mark.parametrize("model_version", all_model_versions())
def test_brachset_names(model_version, branchset_names):
    model = get_model_version(model_version)
    gmcm = model.gmm_logic_tree
    for branch_set in gmcm.branch_sets:
        assert branch_set.short_name == branchset_names[branch_set.tectonic_region_type]['short_name']
        assert branch_set.long_name == branchset_names[branch_set.tectonic_region_type]['long_name']
