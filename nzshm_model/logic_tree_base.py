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

    @abstractclassmethod
    def filtered_branch(self):
        """
        Produce a new filtered branch with the properties of the branch
        """
        pass


# should we have long and short names in the base class?
# should the type for branches be List[Any]?
@dataclass
class BranchSet(ABC):
    short_name: str = 'shortname'
    long_name: str = 'longname'
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
    # should there be placeholder type members?

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

    def __flattened_branches__(self):
        """
        Produce list of Flattened branches, each with a shallow copy of it's slt and fslt parents
        for use in filtering.

        NB this class is never used for serialising models.
        """
        def get_fields(obj):
            return {
                field.name: copy.deepcopy(getattr(obj, field.name))
                for field in fields(obj) if field.name not in ('branches', 'branch_sets')
            }

        lt_fields = get_fields(self)
        for branch_set in self.branch_sets:
            bs_fields = get_fields(branch_set)
            for branch in branch_set.branches:
                bs_lite = branch_set.__class__(**bs_fields, branches=[branch.__class__(weight=1.0)])
                lt_lite = type(self)(**lt_fields)
                # b_fields = get_fields(branch)
                yield branch.filtered_branch(
                    branch_set=bs_lite,
                    logic_tree=lt_lite,
                )

    @classmethod
    def from_branches(cls, branches: Iterator['FilteredBranch']) -> 'LogicTree':
        """
        Build a complete LogicTree from a iterable of branches.

        We expect that all the branhches have come from a single LogicTree.
        """

        def match_branch_set(slt: LogicTree, fb):
            for branch_set in slt.branch_sets:
                if fb.branch_set.short_name == branch_set.short_name:
                    return branch_set

        version = None
        for fb in branches:
            # ensure an slt
            if version is None:
                logic_tree = cls(version=fb.logic_tree.version, title=fb.logic_tree.title)
                version = fb.logic_tree.version
            else:
                assert version == fb.logic_tree.version

            # ensure an branch_set
            bs = match_branch_set(logic_tree, fb)
            if not bs:
                bs = fb.branch_set.__class__(short_name=fb.branch_set.short_name, long_name=fb.branch_set.long_name)
                logic_tree.branch_sets.append(bs)
            bs.branches.append(fb.to_branch())
        return logic_tree

    
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
    

@dataclass
class FilteredBranch(Branch, metaclass=ABCMeta):
    logic_tree: 'LogicTree'
    branch_set: 'BranchSet'

    def to_branch(self) -> Branch:
        branch_attributes = {k: v for k, v in self.__dict__.items() if k not in ('branch_set', 'logic_tree')}
        return type(self.branch_set.branches[0])(**branch_attributes)
