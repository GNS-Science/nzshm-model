import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Union, Type

import dacite

from nzshm_model.psha_adapter import PshaAdapterInterface


@dataclass
class Branch:
    gsim_clsname: str
    gsim_args: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0


@dataclass
class BranchSet:
    tectonic_region_type: str
    branches: List[Branch] = field(default_factory=list)


@dataclass
class GMCMLogicTree:
    version: str = ''
    title: str = ''
    branch_sets: List[BranchSet] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict) -> 'GMCMLogicTree':
        return dacite.from_dict(data_class=GMCMLogicTree, data=data, config=dacite.Config(strict=True))

    @staticmethod
    def from_json(json_path: Union[Path, str]) -> 'GMCMLogicTree':
        with Path(json_path).open() as jsonfile:
            data = json.load(jsonfile)
        return GMCMLogicTree.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs):
        return provider(gmcm_logic_tree=self)
