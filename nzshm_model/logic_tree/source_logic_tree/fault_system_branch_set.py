from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List

from .branch_attribute import BranchAttributeSpec, BranchAttributeValue


@dataclass
class BranchSetSpec:
    short_name: str
    long_name: str
    branches: List['BranchAttributeValue'] = field(default_factory=list)


@dataclass
class BranchSetBase:
    short_name: str
    long_name: str
    branches: List[Any] = field(
        default_factory=list
    )  # we use 'Any' so subclassed version implementations will override typing

    def validate_weights(self) -> bool:
        weight = 0.0
        for b in self.branches:
            weight += b.weight
        return weight == 1.0

    def derive_spec(self) -> BranchSetSpec:
        fslt_spec = BranchSetSpec(short_name=self.short_name, long_name=self.long_name)

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
