"""
Classes for deserialising NRML XML hazard into python dataclasses.

Should work for both GMM models and for Source Rate models.

ref https://github.com/gem/oq-nrmllib/blob/master/openquake/nrmllib/schema/hazard/logic_tree.xsd

NB: runzi.execute.openquake.util.oq_build_sources.py module contains code that
write source XML on the fly, using SLT python modules as inputs.

"""

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path, PurePath
from typing import Any, Iterator, List, Union

from lxml import objectify

NRML_NS = None
VALID_NRML_NS = ["http://openquake.org/xmlns/nrml/0.4", "http://openquake.org/xmlns/nrml/0.5"]

# UNCERTAINTY_MODEL_CLASSNAME = 'GenericUncertaintyModel'


def get_nrml_namespace(element):
    namespaces = element.nsmap
    if namespaces[None] in VALID_NRML_NS:
        return namespaces[None]
    raise ValueError(f"the element {element} does not use a supported NRML namespace.")


@dataclass
class GenericUncertaintyModel:
    text: str
    parent: "LogicTreeBranch"

    @classmethod
    def from_node(cls, node):
        return GenericUncertaintyModel(parent=node, text=node.text.strip())

    def path(self) -> PurePath:
        return PurePath(self.text, self.parent.path())


@dataclass
class GroundMotionUncertaintyModel(GenericUncertaintyModel):
    gmpe_name: str
    arguments: List[str]

    @classmethod
    def from_node(cls, node, parent):
        lines = node.text.split("\n")
        return GroundMotionUncertaintyModel(
            parent=parent,
            text=node.text.strip(),
            gmpe_name=lines[0].strip(),
            arguments=[arg.strip() for arg in lines[1:]],
        )


@dataclass
class SourcesUncertaintyModel(GenericUncertaintyModel):
    source_files: List[str]

    @classmethod
    def from_node(cls, node, parent):
        lines = node.text.split()  # splitting on whitespace
        return SourcesUncertaintyModel(
            parent=parent, text=node.text.strip(), source_files=[arg.strip() for arg in lines]
        )


@dataclass
class LogicTreeBranch:
    parent: "LogicTreeBranchSet"
    branchID: str
    uncertainty_models: List[Any] = field(default_factory=list)
    uncertainty_weight: float = 1.0

    @classmethod
    def from_parent(cls, ltbs, parent):
        def uncertainty_models(ltb, parent, uncertainty_type) -> Iterator[GenericUncertaintyModel]:
            for um in ltb.findall('nrml:uncertaintyModel', namespaces=NRML_NS):
                # here we allow client to override the class for different uncertainty model types,
                yield uncertainty_type.from_node(um, parent)

        def uncertainty_weight(ltb) -> float:
            uws = list(ltb.findall('nrml:uncertaintyWeight', namespaces=NRML_NS))
            if len(uws) == 1:
                return float(uws[0])
            raise ValueError("expecting exactly one uncertaintyWeight child, got {len(uws)}")

        for ltb in ltbs.iterchildren():
            _instance = LogicTreeBranch(
                parent=parent, branchID=ltb.get('branchID'), uncertainty_weight=uncertainty_weight(ltb)
            )
            _instance.uncertainty_models = list(uncertainty_models(ltb, _instance, parent.uncertainty_class()))
            yield _instance

    def path(self) -> PurePath:
        return PurePath(self.branchID, self.parent.path())


@dataclass
class LogicTreeBranchSet:
    parent: "LogicTreeBranch"
    branchSetID: str  # assert ltbs.get('branchSetID') == "bs_crust"
    uncertaintyType: str  # assert ltbs.get('uncertaintyType') == "gmpeModel"
    applyToTectonicRegionType: str  # assert ltbs.get('applyToTectonicRegionType') == "Active Shallow Crust"

    branches: List['LogicTreeBranch'] = field(default_factory=list)

    @classmethod
    def from_parent(cls, logic_tree, parent):
        # use of xpath here let's us ignore internediate elements such as logicTreeBranchingLevel in nrml/0.5
        for ltbs in logic_tree.xpath('//nrml:logicTreeBranchSet', namespaces=NRML_NS):
            _instance = LogicTreeBranchSet(
                parent=parent,
                branchSetID=ltbs.get('branchSetID'),
                uncertaintyType=ltbs.get('uncertaintyType'),
                applyToTectonicRegionType=ltbs.get('applyToTectonicRegionType'),
            )
            _instance.branches = list(LogicTreeBranch.from_parent(ltbs, _instance))
            yield (_instance)

    def uncertainty_class(self):
        if self.uncertaintyType == "gmpeModel":
            return GroundMotionUncertaintyModel
        if self.uncertaintyType == "sourceModel":
            return SourcesUncertaintyModel
        return GenericUncertaintyModel

    def path(self) -> PurePath:
        return PurePath(self.branchSetID, self.parent.path())


@dataclass
class LogicTree:
    logicTreeID: str
    branch_sets: List['LogicTreeBranchSet'] = field(default_factory=list)

    @classmethod
    def from_parent(cls, root):
        for lt in root.xpath('/nrml:nrml/nrml:logicTree', namespaces=NRML_NS):
            _instance = LogicTree(logicTreeID=lt.get('logicTreeID'))
            _instance.branch_sets = list(LogicTreeBranchSet.from_parent(lt, _instance))
            yield _instance

    def path(self) -> PurePath:
        return PurePath(self.logicTreeID)


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
