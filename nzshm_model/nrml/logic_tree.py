"""
Classes for unserialising NRML XML into python dataclasses
"""

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, Iterable, List, Union
from pathlib import Path
from lxml import objectify

NS = {'nrml':'http://openquake.org/xmlns/nrml/0.4'}


@dataclass
class LogicTreeBranch:
    uncertainty_models: List[str]
    uncertainty_weight: float = 1.0

    @classmethod
    def from_logic_tree_branch_set(cls, ltbs):
        for ltb in ltbs.iterchildren():
            ums = []
            for um in ltb.findall('nrml:uncertaintyModel', namespaces=NS):
                ums.append(um.text)

            for wm in ltb.findall('nrml:uncertaintyWeight', namespaces=NS):
                # print(wm.text)
                pass

            yield LogicTreeBranch(uncertainty_models=ums, uncertainty_weight=0.0)


@dataclass
class LogicTreeBranchSet:
    branchSetID: str        # assert ltbs.get('branchSetID') == "bs_crust"
    uncertaintyType: str    # assert ltbs.get('uncertaintyType') == "gmpeModel"
    # assert ltbs.get('applyToTectonicRegionType') == "Active Shallow Crust"
    applyToTectonicRegionType: str  
        
    branches: List['LogicTreeBranch'] = field(default_factory=list)

    @classmethod
    def from_logic_tree(cls, logic_tree):
        for ltbs in logic_tree.iterchildren():
            yield LogicTreeBranchSet(
                branchSetID = ltbs.get('branchSetID'), 
                uncertaintyType = ltbs.get('uncertaintyType'),
                applyToTectonicRegionType = ltbs.get('applyToTectonicRegionType'),
                branches=list(LogicTreeBranch.from_logic_tree_branch_set(ltbs))
            )
            # print(ltbs.tag, ltbs.get('uncertaintyType'), ltbs.get('uncertaintyType'))    


@dataclass
class LogicTree:
    logicTreeID: str
    branch_sets: List['LogicTreeBranchSet'] = field(default_factory=list)

    @classmethod
    def from_root(cls, root):
        for lt in root.xpath('/nrml:nrml/nrml:logicTree', namespaces=NS):
            yield LogicTree(
                logicTreeID=lt.get('logicTreeID'),
                branch_sets=list(LogicTreeBranchSet.from_logic_tree(lt))
            )


@dataclass
class NrmlDocument:
    logic_trees: List['LogicTree'] = field(default_factory=list)

    @classmethod
    def from_xml_file(cls, filepath: Union[Path, str]):
        gmm_tree = objectify.parse(filepath)
        root = gmm_tree.getroot()
        return NrmlDocument(
            logic_trees=LogicTree.from_root(root)
        )
