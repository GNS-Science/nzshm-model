"""
Defines source logic tree structures used in NSHM.
"""

import copy
import warnings
from dataclasses import dataclass, field
from typing import List, Tuple, Union

from nzshm_model.logic_tree.correlation import Correlation, LogicTreeCorrelations
from nzshm_model.logic_tree.logic_tree_base import Branch, BranchSet, FilteredBranch, LogicTree

from . import BranchAttributeValue
from .fault_system_branch_set import BranchSetSpec
from .version1 import SourceLogicTree as SourceLogicTreeV1


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
    tectonic_region_types: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if not isinstance(self.tectonic_region_types, tuple):
            raise TypeError("tectonic_region_types must be a tuple")

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

    @property
    def registry_identity(self):
        nrmls = sorted([s.nrml_id for s in self.sources])
        return "|".join(nrmls)


# TODO: protect from users changing tectonic_region_types
@dataclass
class SourceBranchSet(BranchSet[SourceBranch]):
    """A list of Source Branches.

    Attributes:
        branches: list of branches.
    """

    branches: List[SourceBranch] = field(default_factory=list)

    def __post_init__(self):
        trts = {frozenset(branch.tectonic_region_types) for branch in self.branches}
        if len(trts) > 1:
            raise ValueError("all tectonic_region_types in a branch set must be the same")

    @property
    def tectonic_region_types(self) -> Tuple[str, ...]:
        return self.branches[0].tectonic_region_types if self.branches else ()


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
class SourceLogicTree(LogicTree['SourceFilteredBranch']):
    """A dataclass representing a source logic tree

    Attributes:
        branch_sets: list of branch sets in this tree
        logic_tree_version: constant = 2

    """

    branch_sets: List[SourceBranchSet] = field(default_factory=list)  # branch_sets for this logic tree
    logic_tree_version: Union[int, None] = 2

    def __post_init__(self) -> None:

        # check that sources are defined correctly
        self._check_sources()
        super().__post_init__()

    def _check_sources(self):
        for branch in self:
            if not branch.sources:
                raise ValueError("every branch must have at least one source")
            for source in branch.sources:
                if isinstance(source, DistributedSource) and source.type != "distributed":
                    raise ValueError("source type DistributedSource does not match type member")
                if isinstance(source, InversionSource) and source.type != "inversion":
                    raise ValueError("source type DistributedSource does not match type member")

    def derive_spec(self) -> SourceLogicTreeSpec:
        raise NotImplementedError()
        # slt_spec = SourceLogicTreeSpec()
        # for fslt in self.fault_systems:
        #     slt_spec.fault_systems.append(FaultSystemLogicTree.derive_spec(fslt))
        # return slt_spec

    @staticmethod
    def from_source_logic_tree(original_slt: "SourceLogicTreeV1") -> "SourceLogicTree":
        """
        Migrate from old version one of slt.

        Arguments:
            original_slt: a v1 SourceLogicTree instance.

        Returns:
            a new SourceLogicTree instance
        """

        def index_branch(slt_v1, fslt_name, values):
            fslt_names = [fslt.short_name for fslt in slt_v1.fault_system_lts]
            ind_fslt = fslt_names.index(fslt_name)
            fslt_values = [branch.values for branch in original_slt.fault_system_lts[ind_fslt].branches]
            ind_branch = fslt_values.index(values)
            return ind_fslt, ind_branch

        if not isinstance(original_slt, SourceLogicTreeV1):
            raise ValueError(f"supplied object of {type(original_slt)} is not supported.")
        slt = SourceLogicTree(version=original_slt.version, title=original_slt.title)
        for fslt in original_slt.fault_systems:
            new_fslt = SourceBranchSet(short_name=fslt.short_name, long_name=fslt.long_name)
            branch_id = 0
            for branch in fslt.branches:
                new_branch = SourceBranch(
                    values=copy.deepcopy(branch.values), weight=branch.weight, branch_id=str(branch_id)
                )
                branch_id += 1
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

        if original_slt.correlations:
            correlations = []
            for orig_correlation in original_slt.correlations:
                ind_fslt0, ind_branch0 = index_branch(
                    original_slt, orig_correlation.primary_short_name, orig_correlation.primary_values
                )
                ind_fslt1, ind_branch1 = index_branch(
                    original_slt, orig_correlation.secondary_short_name, orig_correlation.secondary_values
                )
                correlations.append(
                    Correlation(
                        primary_branch=slt.branch_sets[ind_fslt0].branches[ind_branch0],
                        associated_branches=[slt.branch_sets[ind_fslt1].branches[ind_branch1]],
                    )
                )
            slt.correlations = LogicTreeCorrelations(correlations)

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
