#! python slt_config.py

"""
Functions for converting SLT config .py files as used in Runzi and THP etc into the standardised nzshm-model form.

NB: this is needed only for version 1 logic trees, Version 2 are defined directly in JSON.
"""

import copy
import importlib.util
import warnings
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Union

from nzshm_model.logic_tree.source_logic_tree import BranchAttributeValue
from nzshm_model.logic_tree.source_logic_tree.version1 import (
    Branch,
    FaultSystemLogicTree,
    SourceLogicTree,
    SourceLogicTreeCorrelation,
)

try:
    from .toshi_api import solution_rupt_set_id, toshi_api
except ModuleNotFoundError:
    warnings.warn(
        "warning Toshi API module dependency not available, maybe you want to install with nzshm-model[toshi]"
    )


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
            return BranchAttributeValue(name='bN', long_name='bN pair', value=[float(_b[1:]), float(_n[1:])])
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
    if ", N" in tag and ", b" in tag:
        tag = tag.replace(", b", "^b")
    tag = tag.replace("Hik ", "Hik")
    tag = tag.replace("Puy ", "Puy")
    itms = tag.split(' ')

    for itm in itms:
        itm = itm.replace(',', '')  # remove commas

        if itm == 'hiktlck':
            yield BranchAttributeValue(name='dm', long_name='deformation model', value='TL')  # Trench Locked
            continue
        if itm == 'hiktcrp':
            yield BranchAttributeValue(name='dm', long_name='deformation model', value='TC')  # Trench Creeping
            continue
        if itm[:3].upper() in ["HIK", "PUY"]:
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
            yield BranchAttributeValue(name='dm', long_name='deformation model', value=itm)
            continue

        if itm in 'TI, TD':
            yield BranchAttributeValue(name='td', long_name='time dependent', value=(itm == "TD"))
            continue

        other = common_tags(itm)
        if other:
            yield other


def decompose_slab_tag(tag) -> Iterable:
    """used for SLAB. There is only one slab model in our logic tree"""
    return [
        BranchAttributeValue(name='r', long_name='earthquake rates', value='uniform'),
        BranchAttributeValue(name='d', long_name='hypocentral depths', value=1),
    ]


def from_config(config_path: Path, version: str = "", title: str = "") -> SourceLogicTree:
    """
    Build an SLT model from a config file, making some assumptions based on NSHM config conventions.
    """
    file_path = Path(config_path)
    module_name = "model"

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    # sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore

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
                        onfault_nrml_id=member['inv_id'],
                        distributed_nrml_id=member['bg_id'],
                    )
                )
            return fslt
        return

    fslts = [
        build_fslt(*group)
        for group in [("PUY", "Puysegur"), ("HIK", "Hikurangi-Kermadec"), ("CRU", "Crustal"), ("SLAB", "Intra-slab")]
    ]

    correlations = (
        build_correlations(module.src_correlations) if 'src_correlations' in dir(module) else []  # type: ignore
    )
    slt = SourceLogicTree(
        version=version,
        title=title,
        fault_system_lts=list(filter(lambda x: x is not None, fslts)),
        correlations=correlations,
    )
    return slt


def build_correlations(src_correlations: Dict[str, Any]) -> List[SourceLogicTreeCorrelation]:
    def select_decompose(group_name):
        if group_name.upper() in ['PUY', 'HIK']:
            return decompose_subduction_tag
        elif group_name.upper() == 'CRU':
            return decompose_crustal_tag
        elif group_name.upper() == 'SLAB':
            return decompose_slab_tag
        else:
            return None

    secondary_group = src_correlations['dropped_group']
    decompose_tag_sec = select_decompose(secondary_group)

    correlations = []
    for cor in src_correlations['correlations']:
        secondary_ind = [c['group'] for c in cor].index(secondary_group)
        primary_ind = int(not secondary_ind)
        decompose_tag_pri = select_decompose(cor[primary_ind]['group'])
        correlations.append(
            SourceLogicTreeCorrelation(
                primary_short_name=cor[primary_ind]['group'].upper(),
                secondary_short_name=secondary_group.upper(),
                primary_values=list(decompose_tag_pri(cor[primary_ind]['tag'])),
                secondary_values=list(decompose_tag_sec(cor[secondary_ind]['tag'])),
            )
        )

    return correlations


def resolve_toshi_source_ids(slt: SourceLogicTree) -> SourceLogicTree:
    new_slt = copy.deepcopy(slt)

    # SKIP_FS_NAMES =['HIK', 'CRU'] #, 'CRU'

    for fslt in new_slt.fault_system_lts:
        # if fslt.short_name in SKIP_FS_NAMES: #CRU
        #     continue
        if fslt:  # fslt can be None
            for branch in fslt.branches:
                nrml_info = toshi_api.get_source_from_nrml(branch.onfault_nrml_id)
                # print(nrml_info)
                branch.inversion_solution_id = nrml_info.solution_id
                branch.inversion_solution_type = nrml_info.typename
                if nrml_info.solution_id is not None:
                    branch.rupture_set_id = solution_rupt_set_id(nrml_info.solution_id)
                # print(branch) #, end='', flush=True)
                # print('.', end='', flush=True)
    return new_slt
