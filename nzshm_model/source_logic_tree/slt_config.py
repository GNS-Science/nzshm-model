#! python slt_config.py

from typing import Dict, Generator, Iterable, Union

from nzshm_model.source_logic_tree.logic_tree import BranchAttributeValue


def get_config_groups(logic_tree_permutations) -> Generator:
    for permutation in logic_tree_permutations[0][0]['permute']:
        yield permutation


def get_config_group(logic_tree_permutations: Iterable, group_tag: str) -> Union[Dict, None]:
    for group in get_config_groups(logic_tree_permutations):
        if group['group'].upper() == group_tag.upper():
            return group
    return None


def get_config_group_tag_permutations(logic_tree_permutations: Iterable, group_tag: str) -> Generator:
    group = get_config_group(logic_tree_permutations, group_tag)
    if group:
        for member in group['members']:
            yield member['tag']


def common_tags(itm) -> Union[BranchAttributeValue, None]:
    if itm[0] == 'N':
        _n, _b = itm.split('^')
        return BranchAttributeValue(name='bN', long_name='bN pair', value=(float(_b[1:]), float(_n[1:])))
    if itm[0] == 'C':
        return BranchAttributeValue(name='C', long_name='area-magnitude scaling', value=float(itm[1:]))
    if itm[0] == 's':
        return BranchAttributeValue(name='s', long_name='moment rate scaling', value=float(itm[1:]))
    return None


def decompose_subduction_tag(tag) -> Generator:
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


def decompose_crustal_tag(tag) -> Generator:
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
