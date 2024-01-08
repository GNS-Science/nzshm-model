import copy
import json
from abc import ABC, abstractclassmethod, ABCMeta
from pathlib import Path
from dataclasses import dataclass, field, asdict, fields
from typing import Any, Dict, Generator, List, Union, Type, Iterator

import dacite

from nzshm_model.psha_adapter import PshaAdapterInterface


# no default value for weight out of convenience since the subclasses have default values for their own members.
# What do we think?
@dataclass
class Branch(ABC):
    weight: float


# should we have long and short names in the base class?
# should the type for branches be List[Any]?
@dataclass
class BranchSet(ABC):
    branches: List[Branch] = field(default_factory=list)

    def validate_weights(self) -> bool:
        weight = 0.0
        for b in self.branches:
            weight += b.weight
        return weight == 1.0


@dataclass
class LogicTree(ABC):
    title: str = ''
    version: str = ''
    branch_sets: List[BranchSet] = field(default_factory=list)

    @classmethod
    def from_json(cls, json_path: Union[Path, str]) -> 'LogicTree':
        with Path(json_path).open() as jsonfile:
            data = json.load(jsonfile)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict) -> 'LogicTree':
        return dacite.from_dict(data_class=cls, data=data, config=dacite.Config(strict=True))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    # would like this to actully do the work, but not sure how to pass the logic trees wihtout knowning the type.
    # Could check for type in PshaAdaptorInterface, but then we have a circular import.
    @abstractclassmethod
    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs):
        pass

    # can we impliment the logic in the baseclass? Problem is that we need to create concrete objects of derived type
    @abstractclassmethod
    def __flattened_branches__(self):
        pass
        # """
        # Produce list of Flattened branches, each with a shallow copy of it's slt and fslt parents
        # for use in filtering.

        # NB this class is never used for serialising models.
        # """
        # def get_fields(obj):
        #     return {
        #         field.name: copy.deepcopy(getattr(obj, field.name))
        #         for field in fields(obj) if field.name != 'branches'
        #     }

        # for branch_set in self.branch_sets:
        #     bs_fields = get_fields(branch_set)
        #     for branch in branch_set.branches:
        #         bs_lite = BranchSet(**bs_fields)
        #         lt_lite = LogicTree(
        #             title=self.title, version=self.version, logic_tree_version=self.logic_tree_version
        #         )
        #         b_fields = get_fields(branch)
        #         yield FilteredBranch(
        #             branch_set=bs_lite,
        #             logic_tree=lt_lite,
        #             **b_fields,
        #         )
    
    def __iter__(self):
        self.__current_branch = 0
        self.__branch_list = list(self.__flattened_branches__())
        return self

    def __next__(self):
        if self.__current_branch >= len(self.__branch_list):
            raise StopIteration
        else:
            self.__current_branch += 1
            return self.__branch_list[self.__current_branch - 1]
    
    @staticmethod
    @abstractclassmethod
    def from_branches(branches: Iterator['FilteredBranch']) -> 'LogicTree':
        pass

@dataclass
class FilteredBranch(Branch, metaclass=ABCMeta):
    branch_set: 'BranchSet'
    logic_tree: 'LogicTree'

    def to_branch(self) -> Branch:
        branch_attributes = {k: v for k, v in self.__dict__.items() if k not in ('branch_set', 'logic_tree')}
        return type(self.branch_set.branches[0])(**branch_attributes)
