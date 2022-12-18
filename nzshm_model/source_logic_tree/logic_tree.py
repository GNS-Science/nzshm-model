#! logic_tree.py

"""
Classes to define logic tree structures
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Union


@dataclass
class BranchAttributeSpec:
    name: str
    long_name: str
    value_options: List[Any] = field(default_factory=list)


@dataclass(frozen=True)
class BranchAttributeOption:
    name: str
    long_name: str
    value: Any


@dataclass
class BranchAttributeValue:
    name: str
    long_name: str
    value: Any = None

    @staticmethod
    def from_branch_attribute(ba: BranchAttributeSpec, value):
        return BranchAttributeValue(ba.name, ba.long_name, value)

    @staticmethod
    def all_from_branch_attribute(ba: BranchAttributeSpec):
        for opt in ba.value_options:
            yield BranchAttributeValue(ba.name, ba.long_name, opt)

    def __repr__(self):
        return f"{self.name}{self.value}"


@dataclass
class Branch:
    values: List[BranchAttributeValue]
    weight: float = 1.0
    onfault_nrml_id: Union[str, None] = ""
    distributed_nrml_id: Union[str, None] = ""
    inversion_solution_id: Union[str, None] = ""
    inversion_solution_type: Union[str, None] = ""


@dataclass
class FaultSystemLogicTreeSpec:
    short_name: str
    long_name: str
    branches: List['BranchAttributeValue'] = field(default_factory=list)


@dataclass
class FaultSystemLogicTree:
    short_name: str
    long_name: str
    branches: List['Branch'] = field(default_factory=list)

    def validate_weights(self) -> bool:
        weight = 0.0
        for b in self.branches:
            weight += b.weight
        return weight == 1.0

    def derive_spec(self) -> FaultSystemLogicTreeSpec:
        fslt_spec = FaultSystemLogicTreeSpec(short_name=self.short_name, long_name=self.long_name)

        options: Dict[str, set] = {}

        # extract unique values in to options
        for branch in self.branches:
            # iterate all the branches, yielding the unique  branch options
            # print('branch', branch)
            for value in branch.values:
                if value.name not in options.keys():
                    options[value.name] = set([])
                val = value.value
                if isinstance(val, list):  # make it hashable
                    val = tuple(val)
                bao = BranchAttributeOption(value.name, value.long_name, val)
                options[value.name].add(bao)

        # print(options)

        def option_values(options: Dict) -> Generator:
            # boil down the options values
            ret = {}
            for key, opt in options.items():
                if key not in ret:
                    ret[key] = BranchAttributeSpec(key, list(opt)[0].long_name)

                values = []
                for val in opt:
                    values.append(val.value)
                ret[key].value_options = sorted(values)

            for key, bas in ret.items():
                yield bas

        fslt_spec.branches = list(option_values(options))

        return fslt_spec


class SourceLogicTreeCorrelation:
    """
    List[SourceLogicTreeBranch]: branch_sets
    """

    pass


@dataclass
class SourceLogicTreeSpec:
    fault_system_branches: List[FaultSystemLogicTreeSpec] = field(default_factory=list)


@dataclass
class SourceLogicTree:
    version: str
    title: str
    fault_system_branches: List[FaultSystemLogicTree] = field(default_factory=list)
    correlations: List[SourceLogicTreeCorrelation] = field(
        default_factory=list
    )  # to use for weighting when logic trees are correlated

    def derive_spec(self) -> SourceLogicTreeSpec:
        slt_spec = SourceLogicTreeSpec()
        for fslt in self.fault_system_branches:
            slt_spec.fault_system_branches.append(FaultSystemLogicTree.derive_spec(fslt))
        return slt_spec
