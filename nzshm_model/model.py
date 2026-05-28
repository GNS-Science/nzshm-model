"""
NshmModel class describes a complete National Seismic Hazard Model.
"""

import importlib.resources as resources
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Generic

from nzshm_model.logic_tree import GMCMLogicTree, SourceBranchSet, SourceLogicTree
from nzshm_model.logic_tree.source_logic_tree import SourceLogicTreeV1
from nzshm_model.model_versions import versions
from nzshm_model.psha_adapter import PshaAdapterMixin
from nzshm_model.psha_adapter.hazard_config_factory import hazard_config_class_factory

from .psha_adapter.hazard_config import HazardConfig, HazardConfigType

RESOURCES_PATH = resources.files('nzshm_model.resources')

SLT_SOURCE_PATH = RESOURCES_PATH / "SRM_JSON"
GMM_JSON_SOURCE_PATH = RESOURCES_PATH / "GMM_JSON"
GMM_SOURCE_PATH = RESOURCES_PATH / "GMM_LTs"
HAZARD_CONFIG_PATH = RESOURCES_PATH / "HAZARD_CONFIG_JSON"


class NshmModel(PshaAdapterMixin, Generic[HazardConfigType]):
    """
    An NshmModel instance represents a complete National Seismic Hazard Model version.
    """

    def __init__(
        self,
        version: str,
        title: str,
        source_logic_tree: SourceLogicTree,
        gmcm_logic_tree: GMCMLogicTree,
        hazard_config: HazardConfig,
    ):
        """
        Arguments:
            version: Describes version of the model being developed / used.
            tite: A title for the model.
            source_logic_tree: The seismicity rate model (SRM) logic tree.
            gmcm_logic_tree: The ground motion characterization model (GMCM) logic tree.
            hazard_config: The hazard engine (calculator) configuration.
        """
        self.version = version
        self.title = title
        self.hazard_config = hazard_config
        self.source_logic_tree = source_logic_tree
        self.gmm_logic_tree = gmcm_logic_tree

    @classmethod
    def from_files(
        cls,
        version: str,
        title: str,
        slt_json: str | Path,
        gmm_json: str | Path,
        hazard_config_json: str | Path,
    ) -> 'NshmModel[HazardConfigType]':
        """
        Create a new NshmModel instance from files.

        NB library users will typically never use this, rather they will obtain a model instance
        using static method: `get_model_version`.
        """

        # backwards compatibility for v1 SourceLogicTree (v1 has no logic_tree_version key)
        data = NshmModel._slt_data_from_file(slt_json)
        if data.get("logic_tree_version") is None:
            source_logic_tree = NshmModel._source_logic_tree_from_v1_json(slt_json)
        else:
            source_logic_tree = SourceLogicTree.from_json(slt_json)
        gmcm_logic_tree = GMCMLogicTree.from_json(gmm_json)
        HazardConfigClass = hazard_config_class_factory.get_hazard_config_class_from_file(hazard_config_json)
        hazard_config = HazardConfigClass.from_json(hazard_config_json)
        return cls(version, title, source_logic_tree, gmcm_logic_tree, hazard_config)

    @staticmethod
    def _slt_data_from_file(filepath: str | Path) -> dict[Any, Any]:
        with Path(filepath).open('r') as jsonfile:
            data = json.load(jsonfile)
        return data

    @staticmethod
    def _source_logic_tree_from_v1_json(filepath: str | Path) -> SourceLogicTree:
        """
        Create a SourceLogicTree from an old v1 json file; convert to new type.

        Arguments:
            filepath: the path to the json file specifying the source logic tree

        Returns:
            a source logic tree

        """
        return SourceLogicTree.from_source_logic_tree(SourceLogicTreeV1.from_json(filepath))

    @classmethod
    def get_model_version(cls, version: str) -> 'NshmModel':
        """
        Retrieve an existing model by its specific version

        Examples:
            >>> from nzshm_model import NshmModel
            >>> model = NshmModel.get_model_version("NSHM_v1.0.4")
            >>> print(model.title)
            >>>
            NSHM version 1.0.4, corrected fault geometry

        Parameters:
            version: The unique identifier for the model version.

        Raises:
            ValueError: when the version does not exist.

        Returns:
            the model instance.
        """

        spec = versions.get(version)
        if spec is None:
            raise ValueError(f"{version} is not a valid model version.")

        return cls.from_files(
            version=spec.version,
            title=spec.title,
            slt_json=str(SLT_SOURCE_PATH / spec.slt_json),
            gmm_json=str(GMM_JSON_SOURCE_PATH / spec.gmm_json),
            hazard_config_json=str(HAZARD_CONFIG_PATH / spec.hazard_config_json),
        )

    def get_source_branch_sets(self, short_names: list[str] | str | None = None) -> Iterator['SourceBranchSet']:
        """
        get an iterator for the SourceBranchSets matching the specified branch set(s)

        Examples:
            >>>  model = get_model_version("NSHM_v1.0.4")
            >>>  for branch_set in model.get_source_branch_sets(['CRU', 'PUY']):
                    print(branch_set.short_name, len(branch_set.branches))
            >>>
            CRU 36
            PUY 3

        Parameters:
            short_names: list of short_names for branch_set(s) (eg. 'HIK', 'CRU', 'PUY', 'SLAB')

        Raises:
            ValueError: when a branch short_name is not found.

        Yields:
            iterator of branch_set objects
        """
        if isinstance(short_names, str):
            list_short_names: list[str] = [short_names]
        else:
            list_short_names = short_names if short_names is not None else []

        if not list_short_names:  # User passes either an empty list or None
            yield from self.source_logic_tree.branch_sets
        else:
            known = {bs.short_name for bs in self.source_logic_tree.branch_sets}
            for short_name in list_short_names:
                if short_name not in known:
                    raise ValueError(f"The branch '{short_name}' was not found.")
                yield from (bs for bs in self.source_logic_tree.branch_sets if bs.short_name == short_name)

