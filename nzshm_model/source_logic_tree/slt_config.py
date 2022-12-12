#! python slt_config.py

"""
Functions for converting SLT config .py files as used in Runzi and THP etc into the standardised nzshm-model form.
"""

import importlib.util
from pathlib import Path
from typing import Dict, Generator, Iterable, Union

from nzshm_model.source_logic_tree.logic_tree import Branch, BranchAttributeValue, FaultSystemLogicTree, SourceLogicTree


def get_config_groups(logic_tree_permutations) -> Generator:
    for permutation in logic_tree_permutations[0][0]['permute']:
        yield permutation


def get_config_group(logic_tree_permutations: Iterable, group_tag: str) -> Union[Dict, None]:
    for group in get_config_groups(logic_tree_permutations):
        # print(group["group"], group_tag)
        if group['group'].upper() == group_tag.upper():
            return group
    return None


def get_config_group_tag_permutations(logic_tree_permutations: Iterable, group_tag: str) -> Generator:
    group = get_config_group(logic_tree_permutations, group_tag)
    if group:
        for member in group['members']:
            yield member['tag']


def common_tags(itm) -> Union[BranchAttributeValue, None]:
    try:
        if itm[0] == 'N':
            _n, _b = itm.split('^')
            return BranchAttributeValue(name='bN', long_name='bN pair', value=(float(_b[1:]), float(_n[1:])))
        if itm[0] == 'b':  # in some configs b is stand alone
            return BranchAttributeValue(name='b', long_name='b-value', value=float(itm[1:]))
        if itm[0] == 'C':
            return BranchAttributeValue(name='C', long_name='area-magnitude scaling', value=float(itm[1:]))
        if itm[0] == 's':
            return BranchAttributeValue(name='s', long_name='moment rate scaling', value=float(itm[1:]))
    except ValueError as err:
        print(err)
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
    Examples:
     - "geodetic, TI, N2.7, b0.823 C4.2 s0.66"
     - "Cru_geol, b0.849, C4.1, s0.53"
    """
    tag = tag.replace("Cru_geol", "geologic")
    if ", N" in tag and ", b" in tag:
        tag = tag.replace(", b", "^b")
    itms = tag.split(' ')

    for itm in itms:
        itm = itm.replace(',', '')  # remove commas

        if "geo" in itm:
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


def decompose_slab_tag(tag) -> Generator:
    """used for SLAB"""
    yield tag


def from_config(config_path):
    """
    Build an SLT model from a config file, making some assumptions based on NSHM config conventions.
    """
    file_path = Path(config_path)
    module_name = "model"

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    # sys.modules[module_name] = module
    spec.loader.exec_module(module)

    def build_fslt(group_key, long_name):

        decompose_tag = None
        if group_key in ['PUY', 'HIK']:
            decompose_tag = decompose_subduction_tag
        if group_key == 'CRU':
            decompose_tag = decompose_crustal_tag
        if group_key == 'SLAB':
            decompose_tag = decompose_slab_tag

        group = get_config_group(module.logic_tree_permutations, group_key)

        if group:
            fslt = FaultSystemLogicTree(group_key, long_name)

            for member in group['members']:
                fslt.branches.append(
                    Branch(
                        values=list(decompose_tag(member['tag'])),
                        weight=member['weight'],
                        inversion_source=member['inv_id'],
                        distributed_source=member['bg_id'],
                    )
                )
            return fslt
        return

    fslts = [
        build_fslt(*group)
        for group in [("PUY", "Puysegur"), ("HIK", "Hikurangi-Kermadec"), ("CRU", "Crustal"), ("SLAB", "Intra-slab")]
    ]
    slt = SourceLogicTree(fault_system_branches=fslts)

    return slt
