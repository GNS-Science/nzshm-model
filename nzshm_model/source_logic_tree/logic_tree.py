#! logic_tree.py

"""
Classes to define logic tree structures
"""

from copy import deepcopy
from dataclasses import dataclass, field
from functools import reduce
from itertools import product
from math import isclose
from operator import add, mul
from typing import Any, Dict, Generator, Iterable, List, Union


@dataclass
class BranchAttributeSpec:
    name: str
    long_name: str
    value_options: List[Any] = field(default_factory=list)


@dataclass(frozen=True)
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
                bao = BranchAttributeValue(value.name, value.long_name, val)
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


@dataclass
class SourceLogicTreeCorrelation:
    primary_short_name: str
    secondary_short_name: str
    primary_values: List[BranchAttributeValue]
    secondary_values: List[BranchAttributeValue]

    # these methods enforce set compairson
    def is_primary(self, bavs: Iterable[BranchAttributeValue]) -> bool:
        return set(self.primary_values) == set(bavs)

    def is_secondary(self, bavs: Iterable[BranchAttributeValue]) -> bool:
        return set(self.secondary_values) == set(bavs)


@dataclass
class SourceLogicTreeSpec:
    fault_system_lts: List[FaultSystemLogicTreeSpec] = field(default_factory=list)


@dataclass
class SourceLogicTree:
    version: str
    title: str
    fault_system_lts: List[FaultSystemLogicTree] = field(default_factory=list)
    correlations: List[SourceLogicTreeCorrelation] = field(
        default_factory=list
    )  # to use for selecting branches and re-weighting when logic trees are correlated

    def derive_spec(self) -> SourceLogicTreeSpec:
        slt_spec = SourceLogicTreeSpec()
        for fslt in self.fault_system_lts:
            slt_spec.fault_system_lts.append(FaultSystemLogicTree.derive_spec(fslt))
        return slt_spec


@dataclass
class CompositeBranch:
    """Combination of all fault type branches"""

    branches: List[Branch]
    weight: float = 1.0

    def __post_init__(self) -> None:
        self.weight = reduce(mul, [branch.weight for branch in self.branches])


@dataclass
class FlattenedSourceLogicTree:
    """Flattened source logic tree containing all CompositeBranch combinations"""

    version: str
    title: str
    branches: List[CompositeBranch]

    def __post_init__(self) -> None:
        total_weight = reduce(add, [branch.weight for branch in self.branches])
        if not isclose(total_weight, 1.0):
            raise Exception('logic tree weights do not add to 1.0 (sum is %s)' % total_weight)

    @classmethod
    def from_source_logic_tree(cls, slt: SourceLogicTree):

        slt_copy = deepcopy(slt)  # don't want to change weights of origional logic tree object
        branches = [fslt.branches for fslt in slt_copy.fault_system_lts]

        def yield_cor(branches, slt_copy):
            nnames = [[faultsys_lt.short_name] * len(faultsys_lt.branches) for faultsys_lt in slt_copy.fault_system_lts]
            for cb, names in zip(product(*branches), product(*nnames)):
                has_correlation = False
                for cor in slt_copy.correlations:
                    sindex = names.index(cor.secondary_short_name)
                    if cor.is_secondary(cb[sindex].values):
                        has_correlation = True
                        pindex = names.index(cor.primary_short_name)
                        if cor.is_primary(cb[pindex].values):
                            cb[sindex].weight = 1.0
                            yield CompositeBranch(list(cb))
                if not has_correlation:
                    yield CompositeBranch(list(cb))

        if slt.correlations:
            return cls(slt.version, slt.title, list(yield_cor(branches, slt_copy)))
        else:
            return cls(slt.version, slt.title, [CompositeBranch(list(cb)) for cb in product(*branches)])

    def __repr__(self):
        return f'{self.__class__} title {self.title} number of branches: {len(self.branches)}'
