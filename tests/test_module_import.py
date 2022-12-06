#! test_module_import


class TestStructure:
    def setup(self):
        import nzshm_model

        self.model = nzshm_model

    def test_module_import(self):
        assert self.model is not None

    def test_current_version(self):
        assert self.model.CURRENT_VERSION == "NSHM_1.0.0"

    def test_available_versions(self):
        assert len(self.model.versions) == 1

    def test_version_v1_0_0(self):
        v1_0_0 = self.model.get_model_version(self.model, 'NSHM_1.0.0')

        assert v1_0_0['id'] == 'NSHM_1.0.0'
        assert v1_0_0['model'].slt_config is not None
        assert v1_0_0['model'].slt_config.logic_tree_permutations is not None
