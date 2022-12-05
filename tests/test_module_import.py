#! test_module_import

def get_model_version(model, version_id):
    for model_version in model.versions:
        if model_version['id'] == version_id:
            return model_version


class TestStructure:
    def setup(self):
        import nzshm_model
        self.model = nzshm_model

    def test_module_import(self):
        assert self.model is not None

    def test_current_version(self):
        assert self.model.CURRENT_VERSION == "1.0.0"

    def test_available_versions(self):
        assert len(self.model.versions) == 1

    def test_version_v1_0_0(self):
        v1_0_0 = get_model_version(self.model, '1.0.0')

        assert v1_0_0['id'] == '1.0.0'
        assert v1_0_0['model'].source_logic_tree is not None
        assert v1_0_0['model'].source_logic_tree.logic_tree_permutations is not None
