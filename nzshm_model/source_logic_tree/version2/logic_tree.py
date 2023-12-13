#! logic_tree_version_2.py

"""
Define source logic tree structures used in NSHM.
"""
import copy
import json
import pathlib
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Type, Union

import dacite

from nzshm_model.psha_adapter import PshaAdapterInterface

from .. import BranchAttributeValue
from ..core import FaultSystemLogicTreeBase, FaultSystemLogicTreeSpec
from ..version1 import SourceLogicTree as SourceLogicTreeV1


@dataclass
class InversionSource:
    nrml_id: str
    rupture_rate_scaling: Union[float, None] = None  # TODO: needed at this level??
    inversion_id: Union[str, None] = ""
    rupture_set_id: Union[str, None] = ""
    inversion_solution_type: Union[str, None] = ""
    type: str = "inversion"


@dataclass
class DistributedSource:
    nrml_id: str
    rupture_rate_scaling: Union[float, None] = None  # TODO: needed at this level??
    type: str = "distributed"


@dataclass
class Branch:
    values: List[BranchAttributeValue] = field(default_factory=list)
    sources: List[Union[DistributedSource, InversionSource]] = field(default_factory=list)
    weight: float = 1.0
    rupture_rate_scaling: float = 1.0

    def tag(self):
        return str(self.values)


@dataclass
class FaultSystemLogicTree(FaultSystemLogicTreeBase):
    branches: List[Branch] = field(default_factory=list)


@dataclass
class SourceLogicTreeSpec:
    fault_systems: List[FaultSystemLogicTreeSpec] = field(default_factory=list)


@dataclass
class SourceLogicTree:
    version: str
    title: str
    fault_systems: List[FaultSystemLogicTree] = field(default_factory=list)
    logic_tree_version: Union[int, None] = 2

    # correlations: List[SourceLogicTreeCorrelation] = field(
    #     default_factory=list
    # )  # to use for selecting branches and re-weighting when logic trees are correlated

    def derive_spec(self) -> SourceLogicTreeSpec:
        raise NotImplementedError()
        # slt_spec = SourceLogicTreeSpec()
        # for fslt in self.fault_systems:
        #     slt_spec.fault_systems.append(FaultSystemLogicTree.derive_spec(fslt))
        # return slt_spec

    @staticmethod
    def from_dict(data: Dict):
        ltv = data.get("logic_tree_version")
        if not ltv == 2:
            raise ValueError(f"supplied json `logic_tree_version={ltv}` is not supported.")
        return dacite.from_dict(data_class=SourceLogicTree, data=data, config=dacite.Config(strict=True))

    @staticmethod
    def from_json(json_path: Union[pathlib.Path, str]):
        data = json.load(open(json_path))
        return SourceLogicTree.from_dict(data)

    @staticmethod
    def from_source_logic_tree(original_slt: "SourceLogicTreeV1") -> "SourceLogicTree":
        """
        Migrate from old version slt.
        """
        if not isinstance(original_slt, SourceLogicTreeV1):
            raise ValueError(f"supplied object of {type(original_slt)} is not supported.")
        slt = SourceLogicTree(version=original_slt.version, title=original_slt.title)
        for fslt in original_slt.fault_systems:
            new_fslt = FaultSystemLogicTree(short_name=fslt.short_name, long_name=fslt.long_name)
            for branch in fslt.branches:
                # TODO: handle rate scaling
                new_branch = Branch(values=copy.deepcopy(branch.values), weight=branch.weight)
                if branch.onfault_nrml_id:
                    new_branch.sources.append(
                        InversionSource(
                            nrml_id=branch.onfault_nrml_id,
                            inversion_id=branch.inversion_solution_id,
                            rupture_set_id=branch.rupture_set_id,
                        )
                    )
                if branch.distributed_nrml_id:
                    new_branch.sources.append(DistributedSource(nrml_id=branch.distributed_nrml_id))
                new_fslt.branches.append(new_branch)
            slt.fault_systems.append(new_fslt)
        return slt

    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs):
        return provider(self)

    def __iter__(self):
        self.__current_branch = 0
        self.__branch_list = list(self.__flattened_branches__())
        return self

    def __flattened_branches__(self):
        """
        Produce list of Flattened branches, each with a shallow copy of it's slt and fslt parents
        for use in filtering.

        NB this class is never used for serialising models.
        """
        for fslt in self.fault_systems:
            for branch in fslt.branches:
                fslt_lite = FaultSystemLogicTree(short_name=fslt.short_name, long_name=fslt.long_name)
                slt_lite = SourceLogicTree(
                    title=self.title, version=self.version, logic_tree_version=self.logic_tree_version
                )
                yield FilteredBranch(
                    values=branch.values,
                    sources=copy.deepcopy(branch.sources),
                    weight=branch.weight,
                    fslt=fslt_lite,
                    slt=slt_lite,
                )

    def __next__(self):
        if self.__current_branch >= len(self.__branch_list):
            raise StopIteration
        else:
            self.__current_branch += 1
            return self.__branch_list[self.__current_branch - 1]

    @staticmethod
    def from_branches(branches: Iterator['FilteredBranch']) -> 'SourceLogicTree':
        """
        Build a complete SLT from a iterable od branches.

        We expect that all the branhches have come from a single SLT.
        """

        def match_fslt(slt: SourceLogicTree, fb):
            for fslt in slt.fault_systems:
                if fb.fslt.short_name == fslt.short_name:
                    return fslt

        version = None
        for fb in branches:
            # ensure an slt
            if not version:
                slt = SourceLogicTree(version=fb.slt.version, title=fb.slt.title)
                version = fb.slt.version
            else:
                assert version == fb.slt.version

            # ensure an fslt
            fslt = match_fslt(slt, fb)
            if not fslt:
                fslt = FaultSystemLogicTree(short_name=fb.fslt.short_name, long_name=fb.fslt.long_name)
                slt.fault_systems.append(fslt)
            fslt.branches.append(fb.to_branch())
        return slt


# this should never be serialised, only used for filtering
@dataclass
class FilteredBranch(Branch):
    fslt: 'FaultSystemLogicTree' = FaultSystemLogicTree('shortname', 'longname')
    slt: 'SourceLogicTree' = SourceLogicTree('version', 'title')

    def to_branch(self) -> Branch:
        branch_attributes = {k: v for k, v in self.__dict__.items() if k not in ('fslt', 'slt')}
        return Branch(**branch_attributes)
