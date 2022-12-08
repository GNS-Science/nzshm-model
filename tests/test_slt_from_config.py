#! test_module_import
from nzshm_model.source_logic_tree.slt_config import (
    get_config_groups,
    get_config_group,
    get_config_group_tag_permutations,
    decompose_subduction_tag,
    decompose_crustal_tag,
)
from nzshm_model.source_logic_tree.logic_tree import (
    Branch,
    FaultSystemLogicTree,
)


class TestStructure:
    def setup(self):
        import nzshm_model

        self.model = nzshm_model
        self.model_version = self.model.get_model_version(self.model, 'NSHM_1.0.0')

    def test_slt_groups_v1_0_0(self):
        v1_0_0 = self.model.get_model_version(self.model, 'NSHM_1.0.0')

        groups = list(get_config_groups(v1_0_0['model'].slt_config.logic_tree_permutations))
        for slt in groups:
            print(f'group {slt}')
        assert len(groups) == 4

    def test_slt_get_group(self):
        group = get_config_group(self.model_version['model'].slt_config.logic_tree_permutations, 'HIK')
        print(group)
        assert group['group'] == 'Hik'

    def test_get_config_group_tag_permutations(self):
        group = list(
            get_config_group_tag_permutations(self.model_version['model'].slt_config.logic_tree_permutations, 'HIK')
        )
        print(group)
        assert group[0] == 'Hik TL, N16.5, b0.95, C4, s0.42'

    def test_decompose_crustal_tag_permutations(self):
        group = list(
            get_config_group_tag_permutations(self.model_version['model'].slt_config.logic_tree_permutations, 'CRU')
        )
        print(group)
        print(list(decompose_crustal_tag(group[0])))
        assert len(group) == 36

    def test_decompose_hik_tag_permutations(self):
        group = list(
            get_config_group_tag_permutations(self.model_version['model'].slt_config.logic_tree_permutations, 'HIK')
        )
        print(group)
        print(list(decompose_subduction_tag(group[0])))
        assert len(group) == 9

    def test_decompose_puy_tag_permutations(self):
        group = list(
            get_config_group_tag_permutations(self.model_version['model'].slt_config.logic_tree_permutations, 'PUY')
        )
        print(group)
        print(list(decompose_subduction_tag(group[0])))
        assert len(group) == 3

    def test_assemble_puy(self):

        group_key = 'PUY'
        group = get_config_group(self.model_version['model'].slt_config.logic_tree_permutations, group_key)
        print(group)

        fslt = FaultSystemLogicTree('PUY', 'Puysegur')

        for member in group['members']:
            fslt.branches.append(
                Branch(
                    values=list(decompose_subduction_tag(member['tag'])),
                    weight=member['weight'],
                    inversion_source=member['inv_id'],
                    distributed_source=member['bg_id'],
                )
            )

        print(fslt)

        assert fslt.branches[-1].values[0].value == "0.7"
        assert fslt.branches[-1].values[1].value == (0.902, 4.6)
        assert fslt.branches[-1].values[2].value == 4.0
        assert fslt.branches[-1].values[3].value == 1.72
