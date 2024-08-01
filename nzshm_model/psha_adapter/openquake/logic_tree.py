"""
Classes for deserialising NRML XML hazard into python dataclasses.

Should work for both GMM models and for Source Rate models.

Caveats

 - The outdated nrml schema NRML 0.4 is here:
   https://github.com/gem/oq-nrmllib/blob/master/openquake/nrmllib/schema/hazard/logic_tree.xsd

 - We can't find the NRML 0.5 schema

 - GEM do not enforce XSD schema validation. See https://groups.google.com/g/openquake-users/c/3BO_20hCsgg

 - This example source_model_logic_tree.xml shows an non-compliant source logic tree XML file that
   passes the openquake test suite:

    (https://github.com/gem/oq-engine/blob/6926a784f6026bef206a98cb4410be6c3e3c9273/
    openquake/qa_tests_data/logictree/case_01/source_model_logic_tree.xml)

NB: runzi.execute.openquake.util.oq_build_sources.py module contains code that
write source XML on the fly, using SLT python modules as inputs.

"""

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path, PurePath
from typing import TYPE_CHECKING, Any, Iterator, List, Union

from lxml import objectify

if TYPE_CHECKING:
    from nzshm_model.logic_tree.source_logic_tree import logic_tree as slt

from .uncertainty_models import (
    GenericUncertaintyModel,
    GroundMotionUncertaintyModel,
    NshmSourceUncertaintyModel,
    SourcesUncertaintyModel,
    _strip_whitespace,
)

NRML_NS = None
VALID_NRML_NS = ["http://openquake.org/xmlns/nrml/0.4", "http://openquake.org/xmlns/nrml/0.5"]


def get_nrml_namespace(element):
    namespaces = element.nsmap
    if namespaces[None] in VALID_NRML_NS:
        return namespaces[None]
    raise ValueError(f"the element {element} does not use a supported NRML namespace.")


@dataclass
class LogicTreeBranch:
    parent: "LogicTreeBranchSet"
    branchID: str
    uncertainty_models: List[Any] = field(default_factory=list)
    uncertainty_weight: float = 1.0

    @classmethod
    def from_parent_element(cls, ltbs: objectify.Element, parent: "LogicTreeBranchSet") -> Iterator["LogicTreeBranch"]:
        def uncertainty_models(
            ltb: objectify.Element, parent: "LogicTreeBranch", uncertainty_type
        ) -> Iterator[GenericUncertaintyModel]:
            for um in ltb.findall('nrml:uncertaintyModel', namespaces=NRML_NS):
                # here we allow client to override the class for different uncertainty model types,
                yield uncertainty_type.from_parent_element(um, parent)

        def uncertainty_weight(ltb: objectify.Element) -> float:
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

    @classmethod
    def from_parent_slt(
        cls, slt_ltbs: "slt.SourceBranchSet", parent: "LogicTreeBranchSet"
    ) -> Iterator["LogicTreeBranch"]:
        for ltb in slt_ltbs.branches:
            _instance = LogicTreeBranch(
                parent=parent,
                branchID=str(ltb.values),  # ltb.get('branchID'),
                uncertainty_weight=ltb.weight,  # LogicTreeBranch.uncertainty_weight(ltb)
            )
            _instance.uncertainty_models = list(NshmSourceUncertaintyModel.from_parent_slt(ltb, _instance))
            yield _instance

    def path(self) -> PurePath:
        return PurePath(self.parent.path(), _strip_whitespace(self.branchID))


@dataclass
class LogicTreeBranchSet:
    parent: "LogicTree"
    branchSetID: str  # assert ltbs.get('branchSetID') == "bs_crust"
    uncertaintyType: str  # assert ltbs.get('uncertaintyType') == "gmpeModel"
    applyToTectonicRegionType: str  # assert ltbs.get('applyToTectonicRegionType') == "Active Shallow Crust"

    branches: List['LogicTreeBranch'] = field(default_factory=list)

    @classmethod
    def from_parent_element(cls, logic_tree: objectify.Element, parent: "LogicTree") -> Iterator["LogicTreeBranchSet"]:
        # use of xpath here let's us ignore internediate elements such as logicTreeBranchingLevel in nrml/0.5
        for ltbs in logic_tree.xpath('//nrml:logicTreeBranchSet', namespaces=NRML_NS):
            _instance = LogicTreeBranchSet(
                parent=parent,
                branchSetID=ltbs.get('branchSetID'),
                uncertaintyType=ltbs.get('uncertaintyType'),
                applyToTectonicRegionType=ltbs.get('applyToTectonicRegionType'),
            )
            _instance.branches = list(LogicTreeBranch.from_parent_element(ltbs, _instance))
            yield (_instance)

    @classmethod
    def from_parent_slt(cls, slt: "slt.SourceLogicTree", parent: "LogicTree") -> Iterator["LogicTreeBranchSet"]:
        # assert slt_spec.fault_system_lts[0].short_name == "PUY"
        for ltbs in slt.branch_sets:
            _instance = LogicTreeBranchSet(
                parent=parent,
                branchSetID=ltbs.short_name,
                uncertaintyType="sourceModel",
                applyToTectonicRegionType="",
            )
            _instance.branches = list(LogicTreeBranch.from_parent_slt(ltbs, _instance))
            yield _instance

    def uncertainty_class(self):
        if self.uncertaintyType == "gmpeModel":
            return GroundMotionUncertaintyModel
        if self.uncertaintyType == "sourceModel":
            return SourcesUncertaintyModel
        return GenericUncertaintyModel

    def path(self) -> PurePath:
        return PurePath(self.parent.path(), _strip_whitespace(self.branchSetID))


@dataclass
class LogicTree:
    logicTreeID: str
    branch_sets: List['LogicTreeBranchSet'] = field(default_factory=list)

    @classmethod
    def from_parent_element(cls, root: objectify.Element) -> Iterator["LogicTree"]:
        for lt in root.xpath('/nrml:nrml/nrml:logicTree', namespaces=NRML_NS):
            _instance = LogicTree(logicTreeID=lt.get('logicTreeID'))
            _instance.branch_sets = list(LogicTreeBranchSet.from_parent_element(lt, _instance))
            yield _instance

    def path(self) -> PurePath:
        return PurePath(_strip_whitespace(self.logicTreeID))

    @classmethod
    def from_parent_slt(cls, slt: "slt.SourceLogicTree") -> "LogicTree":
        """
        build nrml instance from old-skool dataclasses instance.
        """
        _instance = LogicTree(logicTreeID=slt.version)
        _instance.branch_sets = list(LogicTreeBranchSet.from_parent_slt(slt, _instance))
        return _instance


@dataclass
class NrmlDocument:
    logic_trees: List[LogicTree] = field(default_factory=list)

    @classmethod
    @lru_cache
    def from_xml_file(cls, filepath: Union[Path, str]) -> "NrmlDocument":
        gmm_tree = objectify.parse(filepath)
        root = gmm_tree.getroot()

        global NRML_NS
        NRML_NS = {'nrml': get_nrml_namespace(root)}
        return NrmlDocument(logic_trees=list(LogicTree.from_parent_element(root)))

    @classmethod
    def from_model_slt(cls, slt) -> "NrmlDocument":
        return NrmlDocument(logic_trees=[LogicTree.from_parent_slt(slt)])
