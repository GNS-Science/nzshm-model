from dataclasses import dataclass, field
from typing import Any, Dict, List, Union
from pathlib import Path

from nzshm_model.psha_adapter import NrmlDocument

def _process_gmm_args(args: List[str]) -> Dict[str, Any]:
    def clean_string(string):
        return string.replace('"','').replace("'",'').strip()

    args_dict = dict()
    for arg in args:
        if '=' in arg:
            k, v = arg.split('=')
            args_dict[clean_string(k)] = clean_string(v)
    
    return args_dict


@dataclass
class Branch:
    gsim_clsname: str
    gsim_args: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0

@dataclass
class BranchSet:
    tectonic_region_type: str
    branches: List[Branch] = field(default_factory=list)

@dataclass
class GMCMLogicTree:
    version: str
    title: str
    branch_sets: List[BranchSet] = field(default_factory=list)

    @staticmethod
    def from_xml(xml_path: Union[Path, str]) -> 'GMCMLogicTree':
        """
        Build a GMCMLogicTree from an OpenQuake nrml gmcm logic tree file.
        """
        doc = NrmlDocument.from_xml_file(xml_path)
        if len(doc.logic_trees) != 1:
            raise ValueError("xml must have only 1 logic tree")

        branch_sets = []
        for branch_set in doc.logic_trees[0].branch_sets:
            branches = []
            for branch in branch_set.branches:
                if len(branch.uncertainty_models) != 1:
                    raise ValueError('gmpe branches must have only one uncertainty model')
                gmpe_name = branch.uncertainty_models[0].gmpe_name.replace('[','').replace(']','')
                branches.append(
                    Branch(
                        gsim_clsname=gmpe_name,
                        gsim_args=_process_gmm_args(branch.uncertainty_models[0].arguments),
                        weight=branch.uncertainty_weight,
                    )
                )
            branch_sets.append(
                BranchSet(
                    tectonic_region_type=branch_set.applyToTectonicRegionType,
                    branches=branches,
                )
            )
        return GMCMLogicTree(
            version='',
            title=doc.logic_trees[0].logicTreeID,
            branch_sets=branch_sets,
        )
