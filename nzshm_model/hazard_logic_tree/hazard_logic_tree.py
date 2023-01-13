#! hazard_logic_tree.py

"""
Classes to define hazard logic trees and gather openquake run info from Toshi
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Union
from nzshm_model.source_logic_tree.logic_tree import CompositeSourceLogicTree
from nzshm_model.source_logic_tree.toshi_api import ToshiApi, API_URL, API_KEY, SourceSolutionMap

@dataclass
class HazardBranch:
    hazard_ids: List[str]
    weight: float

@dataclass
class HazardLogicTree:
    name: str
    branches: List[HazardBranch] = field(default_factory=list)

    @classmethod
    def from_composite_slt(cls, cslt: CompositeSourceLogicTree, gt_ids: List[str]):
        headers = {"x-api-key": API_KEY}
        toshi_api = ToshiApi(API_URL, None, with_schema_validation=False, headers=headers)
        source_solution_map = SourceSolutionMap()
        for id in gt_ids:
            source_solution_map.append(toshi_api.get_hazard_gt(id))
        
        def yield_haz_branches(branches):
            for comp_branch in branches:
                hazard_ids = []
                for branch in comp_branch.branches:
                    hazard_ids.append(
                        source_solution_map.get_solution_id(
                            onfault_nrml_id=branch.inversion_solution_id,
                            distributed_nrml_id=branch.distributed_nrml_id
                        )
                    )
                yield HazardBranch(hazard_ids, comp_branch.weight)

        return cls('', list(yield_haz_branches(cslt.branches)))
