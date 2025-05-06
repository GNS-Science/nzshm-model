"""
Classes for deserialising NRML XML hazard uncertainty models.
"""

from dataclasses import dataclass, field
from pathlib import PurePath
from typing import TYPE_CHECKING, Iterator, List

from lxml import objectify

if TYPE_CHECKING:
    from nzshm_model.logic_tree.source_logic_tree import logic_tree as slt

    from .logic_tree import LogicTreeBranch


def _strip_whitespace(string: str) -> str:
    return ''.join(string.split())


@dataclass
class GenericUncertaintyModel:
    parent: "LogicTreeBranch"
    text: str = ""

    @classmethod
    def from_parent_element(cls, node: objectify.Element, parent: "LogicTreeBranch") -> "GenericUncertaintyModel":
        return GenericUncertaintyModel(parent=parent, text=node.text.strip())

    def path(self) -> PurePath:
        return PurePath(self.parent.path(), _strip_whitespace(self.text))


@dataclass
class GroundMotionUncertaintyModel:
    parent: "LogicTreeBranch"
    gmpe_name: str
    arguments: List[str]
    text: str = ""

    @classmethod
    def from_parent_element(cls, node: objectify.Element, parent: "LogicTreeBranch") -> "GroundMotionUncertaintyModel":
        lines = node.text.split("\n")
        return GroundMotionUncertaintyModel(
            parent=parent,
            text=node.text.strip(),
            gmpe_name=lines[0].strip(),
            arguments=[arg.strip() for arg in lines[1:]],
        )

    def path(self) -> PurePath:
        return PurePath(self.parent.path(), _strip_whitespace(self.text))  # todo unique combination of name + args


@dataclass
class SourcesUncertaintyModel:
    parent: "LogicTreeBranch"
    source_files: List[str]
    text: str = ""

    @classmethod
    def from_parent_element(cls, node: objectify.Element, parent: "LogicTreeBranch") -> "SourcesUncertaintyModel":
        lines = node.text.split()  # splitting on whitespace
        return SourcesUncertaintyModel(
            parent=parent, text=node.text.strip(), source_files=[arg.strip() for arg in lines]
        )

    def path(self) -> PurePath:
        return PurePath(self.parent.path(), _strip_whitespace(self.text))  # todo unique combination of sources


@dataclass
class NshmSourceUncertaintyModel:
    parent: "LogicTreeBranch"
    source_files: List[str] = field(
        default_factory=list
    )  # deferred , we must unpack these from the nrml_id (either direct source or zip file containing sources)
    toshi_nrml_id: str = ""  # in NZSHM22 this is toshi ID
    global_uri: str = ""  # eventually NZSHM or others may publish these as URI resources.
    model_type: str = ""

    @classmethod
    def from_parent_slt(
        cls, ltb: "slt.SourceBranch", parent: "LogicTreeBranch"
    ) -> Iterator["NshmSourceUncertaintyModel"]:
        """resolve to filenames of NRML sources"""
        for source in ltb.sources:
            if source.type == 'inversion':
                yield NshmSourceUncertaintyModel(parent=parent, toshi_nrml_id=source.nrml_id, model_type="FaultSource")
            if source.type == 'distributed':
                yield NshmSourceUncertaintyModel(
                    parent=parent, toshi_nrml_id=source.nrml_id, model_type="DistributedSource"
                )

    def path(self) -> PurePath:
        return PurePath(self.parent.path(), _strip_whitespace(self.toshi_nrml_id))  # todo unique combination of sources
