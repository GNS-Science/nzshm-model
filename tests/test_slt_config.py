#! test_module_import
from pathlib import Path

import nzshm_model
from nzshm_model.source_logic_tree.logic_tree import Branch, FaultSystemLogicTree
from nzshm_model.source_logic_tree.slt_config import (
    decompose_crustal_tag,
    decompose_subduction_tag,
    from_config,
    get_config_group,
    get_config_group_tag_permutations,
    get_config_groups,
)


class TestStructure:
    def setup(self):
        self.model = nzshm_model.get_model_version('NSHM_1.0.0')

    def test_slt_groups_v1_0_0(self):
        v1_0_0 = self.model
        groups = list(get_config_groups(v1_0_0.slt_config.logic_tree_permutations))
        for slt in groups:
            print(f'group {slt}')
        assert len(groups) == 4

    def test_slt_get_group(self):
        group = get_config_group(self.model.slt_config.logic_tree_permutations, 'HIK')
        print(group)
        assert group['group'] == 'Hik'

    def test_get_config_group_tag_permutations(self):
        group = list(get_config_group_tag_permutations(self.model.slt_config.logic_tree_permutations, 'HIK'))
        print(group)
        assert group[0] == 'Hik TL, N16.5, b0.95, C4, s0.42'

    def test_decompose_crustal_tag_permutations(self):
        group = list(get_config_group_tag_permutations(self.model.slt_config.logic_tree_permutations, 'CRU'))
        print(group)
        print(list(decompose_crustal_tag(group[0])))
        assert len(group) == 36

    def test_decompose_hik_tag_permutations(self):
        group = list(get_config_group_tag_permutations(self.model.slt_config.logic_tree_permutations, 'HIK'))
        print(group)
        print(list(decompose_subduction_tag(group[0])))
        assert len(group) == 9

    def test_decompose_puy_tag_permutations(self):
        group = list(get_config_group_tag_permutations(self.model.slt_config.logic_tree_permutations, 'PUY'))
        print(group)
        print(list(decompose_subduction_tag(group[0])))
        assert len(group) == 3

    def test_assemble_puy(self):

        group_key = 'PUY'
        group = get_config_group(self.model.slt_config.logic_tree_permutations, group_key)
        print(group)

        fslt = FaultSystemLogicTree('PUY', 'Puysegur')

        for member in group['members']:
            fslt.branches.append(
                Branch(
                    values=list(decompose_subduction_tag(member['tag'])),
                    weight=member['weight'],
                    onfault_nrml_id=member['inv_id'],
                    distributed_nrml_id=member['bg_id'],
                )
            )

        print(fslt)

        assert fslt.branches[-1].values[0].value == "0.7"
        assert fslt.branches[-1].values[1].value == (0.902, 4.6)
        assert fslt.branches[-1].values[2].value == 4.0
        assert fslt.branches[-1].values[3].value == 1.72


class TestFromConfig:
    def test_slt_v8(self):
        config = Path(__file__).parent.parent / 'nzshm_model' / 'source_logic_tree' / 'SLT_v8_gmm_v2_final.py'
        slt = from_config(config)
        print(slt)
        assert slt.fault_system_branches[0].branches[-1].values[0].name == 'dm'

    def test_large_SLT_example_A_crustal(self):
        config = Path(__file__).parent / 'fixtures' / 'large_SLT_example_A.py'
        slt = from_config(config)
        print(slt)
        assert slt.fault_system_branches[1].branches[-1].values[0].name == 'dm'
        assert slt.fault_system_branches[1].branches[-1].values[0].value == 'TC'


class TestDecomposeTags:
    def test_large_SLT_example_A_crustal(self):
        decomp = list(decompose_crustal_tag("Cru_geol, b0.849, C4.1, s0.53"))
        print(decomp[0].value)

        assert decomp[0].name == 'dm'
        assert decomp[0].value == 'geologic'
        assert decomp[1].name == 'b'
        assert decomp[1].value == 0.849
        assert decomp[2].name == 'C'
        assert decomp[2].value == 4.1
        assert decomp[3].name == 's'
        assert decomp[3].value == 0.53

    def test_large_SLT_V8_crustal(self):
        decomp = list(decompose_crustal_tag("geodetic, TI, N2.7, b0.823 C4.2 s0.66"))
        assert decomp[0].name == 'dm'
        assert decomp[0].value == 'geodetic'
        assert decomp[1].name == 'td'
        assert decomp[1].value is False
        assert decomp[2].name == 'bN'
        assert decomp[2].value == (0.823, 2.7)
        assert decomp[3].name == 'C'
        assert decomp[3].value == 4.2
        assert decomp[4].name == 's'
        assert decomp[4].value == 0.66
