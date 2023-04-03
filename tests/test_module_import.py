#! test_module_import
import pytest

import nzshm_model


class TestStructure:
    def test_current_version(self):
        assert nzshm_model.CURRENT_VERSION == "NSHM_1.0.0"

    def test_available_versions(self):
        assert len(nzshm_model.versions) == 2

    @pytest.mark.parametrize("model, model_version", [('NSHM_1.0.0', 'NSHM_1.0.0'), ('NSHM_1.0.4', 'NSHM_1.0.4')])
    def test_version_config(self, model, model_version):
        mod = nzshm_model.get_model_version(model)

        assert mod.version == model_version

        assert mod.slt_config is not None
        assert mod.slt_config.logic_tree_permutations is not None

        slt = mod.source_logic_tree()
        assert slt.version == model_version

    def test_get_model_version_unknown(self):
        unknown = nzshm_model.get_model_version('XXX')
        assert unknown is None
