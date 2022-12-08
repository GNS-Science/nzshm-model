#! test_module_import

# import itertools
import collections
from typing import Iterable, Generator, Dict, Union
from nzshm_model.source_logic_tree.logic_tree import (
    BranchAttribute,
    BranchAttributeValue,
    Branch,
    FaultSystemLogicTree,
)


def get_config_groups(logic_tree_permutations) -> Generator:
    for permutation in logic_tree_permutations[0][0]['permute']:
        yield permutation


def get_config_group(logic_tree_permutations: Iterable, group_tag: str) -> Union[Dict, None]:
    for group in get_config_groups(logic_tree_permutations):
        if group['group'].upper() == group_tag.upper():
            return group
    return None


def get_config_group_tag_permutations(logic_tree_permutations: Iterable, group_tag: str):
    group = get_config_group(logic_tree_permutations, group_tag)
    if group:
        for member in group['members']:
            yield member['tag']


def common_tags(itm):
    if itm[0] == 'N':
        _n, _b = itm.split('^')
        return BranchAttributeValue(name='bN', long_name='bN pair', value=(float(_b[1:]), float(_n[1:])))
    if itm[0] == 'C':
        return BranchAttributeValue(name='C', long_name='area-magnitude scaling', value=float(itm[1:]))
    if itm[0] == 's':
        return BranchAttributeValue(name='s', long_name='moment rate scaling', value=float(itm[1:]))


def decompose_subduction_tag(tag):
    """
    "tag": "Hik TL, N16.5, b0.95, C4, s0.42",
    "tag": "Puy 0.7, N4.6, b0.902, C4, s0.28",
    """
    tag = tag.replace(", b", "^b")
    tag = tag.replace("Hik ", "Hik")
    tag = tag.replace("Puy ", "Puy")
    itms = tag.split(' ')

    for itm in itms:
        itm = itm.replace(',', '')  # remove commas
        if itm[:3] in ["Hik", "Puy"]:
            yield BranchAttributeValue(name='dm', long_name='deformation model', value=itm[3:])
            continue

        other = common_tags(itm)
        if other:
            yield other


def decompose_crustal_tag(tag):
    """
    "tag": "geodetic, TI, N2.7, b0.823 C4.2 s0.66",
    """
    tag = tag.replace(", b", "^b")
    itms = tag.split(' ')

    for itm in itms:
        itm = itm.replace(',', '')  # remove commas

        if "geo" == itm[:3]:
            yield BranchAttributeValue(
                name='dm', long_name='deformation model', value_options=['geodetic', 'geologic'], value=itm
            )
            continue

        if itm in 'TI, TD':
            yield BranchAttributeValue(
                name='td', long_name='time dependent', value_options=[True, False], value=(itm == "TD")
            )
            continue

        other = common_tags(itm)
        if other:
            yield other


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
            bavs = list(decompose_subduction_tag(member['tag']))
            fslt.branches.append(Branch(values=bavs, weight=member['weight'], inversion_source=member['inv_id'], distributed_source=member['bg_id']))

        print(fslt)

        assert fslt.branches[-1].values[0].value == "0.7"
        assert fslt.branches[-1].values[1].value == (0.902, 4.6)
        assert fslt.branches[-1].values[2].value == 4.0
        assert fslt.branches[-1].values[3].value == 1.72
