#! branch_attribute.py

"""
Branch structures used in NSHM source logic trees
"""

from dataclasses import field
from typing import Any, List

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

_CONFIG = ConfigDict(extra="forbid", arbitrary_types_allowed=True)


@dataclass(config=_CONFIG)
class BranchAttributeSpec:
    name: str
    long_name: str
    value_options: List[Any] = field(default_factory=list)


@dataclass(frozen=True, config=_CONFIG)
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
