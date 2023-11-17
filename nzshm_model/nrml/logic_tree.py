"""
Classes for deserialising NRML XML into python dataclasses.

Should work for both GMM models and for Source Rate models.

NB: runzi.execute.openquake.util.oq_build_sources.py module contains code that
write source XML on the fly, using SLT python modules as inputs.

"""

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Iterator, List, Union

from lxml import objectify

NRML_NS = None
VALID_NRML_NS = ["http://openquake.org/xmlns/nrml/0.4", "http://openquake.org/xmlns/nrml/0.5"]

UNCERTAINTY_MODEL_CLASSNAME = 'GenericUncertaintyModel'

def get_nrml_namespace(element):
    namespaces = element.nsmap
    if namespaces[None] in VALID_NRML_NS:
        return namespaces[None]
    raise ValueError(f"the element {element} does not use a supported NRML namespace.")


@dataclass
class GenericUncertaintyModel:
    text: str


@dataclass
class LogicTreeBranch:
    branchID: str
    uncertainty_models: List[str]
    uncertainty_weight: float = 1.0

    @classmethod
    def from_parent(cls, ltbs):
        def uncertainty_models(ltb) -> Iterator[GenericUncertaintyModel]:
            for um in ltb.findall('nrml:uncertaintyModel', namespaces=NRML_NS):
                print(um)
                clazz = globals[UNCERTAINTY_MODEL_CLASSNAME]
                yield clazz(text=um.text)

        def uncertainty_weight(ltb) -> float:
            uws = list(ltb.findall('nrml:uncertaintyWeight', namespaces=NRML_NS))
            if len(uws) == 1:
                return float(uws[0])
            raise ValueError("expecting exactly one uncertaintyWeight child, got {len(uws)}")

        for ltb in ltbs.iterchildren():

            yield LogicTreeBranch(
                branchID=ltb.get('branchID'),
                uncertainty_models=list(uncertainty_models(ltb)),
                uncertainty_weight=uncertainty_weight(ltb),
            )


@dataclass
class LogicTreeBranchSet:
    branchSetID: str  # assert ltbs.get('branchSetID') == "bs_crust"
    uncertaintyType: str  # assert ltbs.get('uncertaintyType') == "gmpeModel"
    applyToTectonicRegionType: str  # assert ltbs.get('applyToTectonicRegionType') == "Active Shallow Crust"

    branches: List['LogicTreeBranch'] = field(default_factory=list)

    @classmethod
    def from_parent(cls, logic_tree):
        # use of xpath here let's us ignore internediate elements such as logicTreeBranchingLevel in nrml/0.5
        for ltbs in logic_tree.xpath('//nrml:logicTreeBranchSet', namespaces=NRML_NS):
            yield LogicTreeBranchSet(
                branchSetID=ltbs.get('branchSetID'),
                uncertaintyType=ltbs.get('uncertaintyType'),
                applyToTectonicRegionType=ltbs.get('applyToTectonicRegionType'),
                branches=list(LogicTreeBranch.from_parent(ltbs)),
            )
            # print(ltbs.tag, ltbs.get('uncertaintyType'), ltbs.get('uncertaintyType'))


@dataclass
class LogicTree:
    logicTreeID: str
    branch_sets: List['LogicTreeBranchSet'] = field(default_factory=list)

    @classmethod
    def from_parent(cls, root):
        for lt in root.xpath('/nrml:nrml/nrml:logicTree', namespaces=NRML_NS):
            yield LogicTree(logicTreeID=lt.get('logicTreeID'), branch_sets=list(LogicTreeBranchSet.from_parent(lt)))


@dataclass
class NrmlDocument:
    logic_trees: List['LogicTree'] = field(default_factory=list)

    @classmethod
    @lru_cache
    def from_xml_file(cls, filepath: Union[Path, str]):
        gmm_tree = objectify.parse(filepath)
        root = gmm_tree.getroot()

        global NRML_NS
        NRML_NS = {'nrml': get_nrml_namespace(root)}
        return NrmlDocument(logic_trees=list(LogicTree.from_parent(root)))
