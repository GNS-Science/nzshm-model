#! test_module_import
import nzshm_model


class TestStructure:
    def test_current_version(self):
        assert nzshm_model.CURRENT_VERSION == "NSHM_1.0.0"

    def test_available_versions(self):
        assert len(nzshm_model.versions) == 1

    def test_version_v1_0_0(self):
        v1_0_0 = nzshm_model.get_model_version('NSHM_1.0.0')

        assert v1_0_0.version == 'NSHM_1.0.0'

        assert v1_0_0.slt_config is not None
        assert v1_0_0.slt_config.logic_tree_permutations is not None

        slt = v1_0_0.source_logic_tree()
        assert slt.version == 'SLT_v8'
        assert slt.title == ''

    def test_get_model_version_unknown(self):
        unknown = nzshm_model.get_model_version('XXX')
        assert unknown is None
