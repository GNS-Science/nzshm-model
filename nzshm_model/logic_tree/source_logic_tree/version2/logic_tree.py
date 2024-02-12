#! logic_tree_version_2.py

"""
Define source logic tree structures used in NSHM.
"""
import copy
import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Type, Union

from nzshm_model.logic_tree.logic_tree_base import Branch, BranchSet, FilteredBranch, LogicTree
from nzshm_model.psha_adapter import PshaAdapterInterface

from .. import BranchAttributeValue
from ..core import BranchSetSpec
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
class SourceBranch(Branch):
    values: List[BranchAttributeValue] = field(default_factory=list)
    sources: List[Union[DistributedSource, InversionSource]] = field(default_factory=list)
    rupture_rate_scaling: float = 1.0

    def filtered_branch(self, logic_tree, branch_set):
        return SourceFilteredBranch(logic_tree=logic_tree, branch_set=branch_set, **self.__dict__)

    @property
    def tag(self):
        return str(self.values)


@dataclass
class SourceBranchSet(BranchSet):
    branches: List[SourceBranch] = field(default_factory=list)


@dataclass
class SourceLogicTreeSpec:
    branch_sets: List[BranchSetSpec] = field(default_factory=list)

    @property
    def fault_systems(self):
        """
        API alias for branch_sets
        """
        warnings.warn("Please use branch_sets property instead", DeprecationWarning)
        return self.branch_sets


@dataclass
class SourceLogicTree(LogicTree):
    """The summary line for a class docstring should fit on one line.

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Attributes:
        branch_sets: Description of `attr1`.
        logic_tree_version: Description of `attr2`.

    """

    branch_sets: List[SourceBranchSet] = field(default_factory=list)  # branch_sets for this logic tree
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

    @classmethod
    def from_dict(cls, data: Dict):
        ltv = data.get("logic_tree_version")
        if not ltv == 2:
            raise ValueError(f"supplied json `logic_tree_version={ltv}` is not supported.")
        return super(SourceLogicTree, cls).from_dict(data)

    @staticmethod
    def from_source_logic_tree(original_slt: "SourceLogicTreeV1") -> "SourceLogicTree":
        """
        Migrate from old version slt.
        """
        if not isinstance(original_slt, SourceLogicTreeV1):
            raise ValueError(f"supplied object of {type(original_slt)} is not supported.")
        slt = SourceLogicTree(version=original_slt.version, title=original_slt.title)
        for fslt in original_slt.fault_systems:
            new_fslt = SourceBranchSet(short_name=fslt.short_name, long_name=fslt.long_name)
            for branch in fslt.branches:
                # TODO: handle rate scaling
                new_branch = SourceBranch(values=copy.deepcopy(branch.values), weight=branch.weight)
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
            slt.branch_sets.append(new_fslt)
        return slt

    @property
    def fault_system_lts(self):
        """
        API alias for branch_sets
        """
        warnings.warn("Please use branch_sets property instead", DeprecationWarning)
        return self.branch_sets

    @property
    def fault_systems(self):
        """
        API alias for branch_sets
        """
        warnings.warn("Please use branch_sets property instead", DeprecationWarning)
        return self.branch_sets

    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs):
        return provider(source_logic_tree=self)


@dataclass
class SourceFilteredBranch(FilteredBranch, SourceBranch):
    logic_tree: 'SourceLogicTree' = SourceLogicTree()
    branch_set: 'SourceBranchSet' = SourceBranchSet()

    @property
    def fslt(self) -> SourceBranchSet:
        """
        API alias for branch_set
        """
        warnings.warn("Please use branch_set property instead", DeprecationWarning)
        return self.branch_set

    @property
    def slt(self) -> SourceLogicTree:
        """
        API alias for slt
        """
        warnings.warn("Please use logic_tree property instead", DeprecationWarning)
        return self.logic_tree
