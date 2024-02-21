"""
Defines source logic tree structures used in NSHM.
"""
import copy
import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type, Union

from nzshm_model.logic_tree.logic_tree_base import Branch, BranchSet, FilteredBranch, LogicTree
from nzshm_model.psha_adapter import PshaAdapterInterface

from .. import BranchAttributeValue
from ..core import BranchSetSpec
from ..version1 import SourceLogicTree as SourceLogicTreeV1


@dataclass
class InversionSource:
    """
    A hazard source built from an NSHM Grand Inversion experiment

    Contains the specific identifiers used in NSHM Toshi API.

    Attributes:
        nrml_id: toshi_id for a NRML source file (needed by openquake)
        rupture_rate_scaling: the scaling ratio
        inversion_id: toshi_id for the source inversion solution
        rupture_set_id: toshi_id for the source rupture set
        inversion_solution_type: type (if any) of the source inversion solution
        type: constant "inversion"
    """

    nrml_id: str
    rupture_rate_scaling: Union[float, None] = None  # TODO: needed at this level??
    inversion_id: Union[str, None] = ""
    rupture_set_id: Union[str, None] = ""
    inversion_solution_type: Union[str, None] = ""
    type: str = "inversion"


@dataclass
class DistributedSource:
    """
    A gridded hazard source built from a background (off-fault) seismic rate model

    Contains the specific identifiers used in NSHM Toshi API.

    Attributes:
        nrml_id: toshi_id for a NRML source file (needed by openquake)
        rupture_rate_scaling: the scaling ratio
        type: constant "distributed"
    """

    nrml_id: str
    rupture_rate_scaling: Union[float, None] = None  # TODO: needed at this level??
    type: str = "distributed"


@dataclass
class SourceBranch(Branch):
    """
    A source branch can contain multiple sources.

    Contains the specific identifiers used in NSHM Toshi API.

    Attributes:
        values: list of attribute values that define the branch.
        sources: list of branch sources.
        rupture_rate_scaling: the scaling ratio.
    """

    values: List[BranchAttributeValue] = field(default_factory=list)
    sources: List[Union[DistributedSource, InversionSource]] = field(default_factory=list)
    rupture_rate_scaling: float = 1.0

    def filtered_branch(self, logic_tree: 'LogicTree', branch_set: 'BranchSet') -> 'FilteredBranch':
        """get a filtered branch containing reference to parent instances.

        Arguments:
            logic_tree: the source_logic_tree containing the branch
            branch_set: the branch_set containing the branch

        Returns:
            a SourceFilteredBranch instance
        """
        return SourceFilteredBranch(logic_tree=logic_tree, branch_set=branch_set, **self.__dict__)

    @property
    def tag(self) -> str:
        """tag identifies a branch based on its values (BranchAttributeValue).

        Returns:
            a string representation of the the list of values

        """
        return str(self.values)


@dataclass
class SourceBranchSet(BranchSet):
    """A list of Source Branches.

    Attributes:
        branches: list of branches.
    """

    branches: List[SourceBranch] = field(default_factory=list)


@dataclass
class SourceLogicTreeSpec:
    """Is this used anymore?"""

    branch_sets: List[BranchSetSpec] = field(default_factory=list)

    @property
    def fault_systems(self):
        """
        API alias for branch_sets (deprecated)
        """
        warnings.warn("Please use branch_sets property instead", DeprecationWarning)
        return self.branch_sets


@dataclass
class SourceLogicTree(LogicTree):
    """A dataclass representing a source logic tree

    Attributes:
        branch_sets: list of branch sets in this tree
        logic_tree_version: constant = 2

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
    def from_dict(cls, data: Dict) -> 'LogicTree':
        """build a new instance from a dict represention.

        Arguments:
            data: a dictionary of the SourceLogicTree properties.

        Returns:
            a new SourceLogicTree instance
        """
        ltv = data.get("logic_tree_version")
        if not ltv == 2:
            raise ValueError(f"supplied json `logic_tree_version={ltv}` is not supported.")
        return super(SourceLogicTree, cls).from_dict(data)

    @staticmethod
    def from_source_logic_tree(original_slt: "SourceLogicTreeV1") -> "SourceLogicTree":
        """
        Migrate from old version one of slt.

        Arguments:
            original_slt: a v1 SourceLogicTree instance.

        Returns:
            a new SourceLogicTree instance
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
        API alias for branch_sets (deprecated)
        """
        warnings.warn("Please use branch_sets property instead", DeprecationWarning)
        return self.branch_sets

    @property
    def fault_systems(self):
        """
        API alias for branch_sets (deprecated)
        """
        warnings.warn("Please use branch_sets property instead", DeprecationWarning)
        return self.branch_sets

    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs: Optional[Dict]) -> "PshaAdapterInterface":
        """get a PSHA adapter for this instance.

        Arguments:
            provider: the adapter class
            **kwargs: additional arguments required by the provider class

        Returns:
            a PSHA Adapter instance
        """
        return provider(source_logic_tree=self)


@dataclass
class SourceFilteredBranch(FilteredBranch, SourceBranch):
    """A logic tree source branch with additional properties

    Used to represent a branch that has been pruned (filtered) from a
    complete Source Logic Tree (SLT). The additional properties make the prundd branch
    traceable to its original SLT.

    Attributes:
        logic_tree: the source_logic_tree containing the branch
        branch_set: the branch_set containing the branch

    """

    logic_tree: 'LogicTree' = field(default_factory=SourceLogicTree)
    branch_set: 'BranchSet' = field(default_factory=SourceBranchSet)

    @property
    def fslt(self) -> 'BranchSet':
        """
        API alias for branch_set (deprecated)
        """
        warnings.warn("Please use branch_set property instead", DeprecationWarning)
        return self.branch_set

    @property
    def slt(self) -> 'LogicTree':
        """
        API alias for slt (deprecated)
        """
        warnings.warn("Please use logic_tree property instead", DeprecationWarning)
        return self.logic_tree
