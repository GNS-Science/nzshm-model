#! branch_attribute.py

"""
Branch structures used in NSHM source logic trees
"""

from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field


class BranchAttributeSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    name: str
    long_name: str
    value_options: List[Any] = Field(default_factory=list)


class BranchAttributeValue(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True, frozen=True)

    name: str
    long_name: str
    value: Any = None

    @staticmethod
    def from_branch_attribute(ba: "BranchAttributeSpec", value):
        return BranchAttributeValue(name=ba.name, long_name=ba.long_name, value=value)

    @staticmethod
    def all_from_branch_attribute(ba: "BranchAttributeSpec"):
        for opt in ba.value_options:
            yield BranchAttributeValue(name=ba.name, long_name=ba.long_name, value=opt)

    def __repr__(self):
        return f"{self.name}{self.value}"
