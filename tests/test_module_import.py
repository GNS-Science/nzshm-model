#! test_module_import
import pytest

import nzshm_model


def test_current_version():
    assert nzshm_model.CURRENT_VERSION == "NSHM_v1.0.4"


def test_available_versions():
    assert len(nzshm_model.versions) == 2


@pytest.mark.parametrize("model, model_version", [('NSHM_v1.0.0', 'NSHM_v1.0.0'), ('NSHM_v1.0.4', 'NSHM_v1.0.4')])
def test_version_config(model, model_version):
    mod = nzshm_model.NshmModel.get_model_version(model)
    # mod = nzshm_model.get_model_version(model)

    assert mod.version == model_version


def test_get_model_version_unknown():
    with pytest.raises(ValueError, match='XXX is not a valid model version.'):
        nzshm_model.get_model_version('XXX')


@pytest.mark.parametrize('model_version', [ver for ver in nzshm_model.versions.keys()])
def test_source_logic_tree_in_all_models(model_version):
    current_model = nzshm_model.get_model_version(model_version)
    slt = current_model.source_logic_tree

    old_api_fslt = slt.fault_system_lts[0]
    new_api_fslt = slt.branch_sets[0]

    assert old_api_fslt is new_api_fslt
