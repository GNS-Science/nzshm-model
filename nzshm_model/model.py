"""
NshmModel class describes a complete National Seismic Hazard Model.
"""
import json
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Type, Union

from nzshm_model.logic_tree import GMCMLogicTree, SourceBranchSet, SourceLogicTree
from nzshm_model.logic_tree.source_logic_tree import SourceLogicTreeV1
from nzshm_model.model_versions import versions
from nzshm_model.psha_adapter import PshaAdapterInterface
from nzshm_model.psha_adapter.openquake import NrmlDocument, OpenquakeGMCMPshaAdapter

if TYPE_CHECKING:
    # from nzshm_model import psha_adapter
    from nzshm_model.psha_adapter.openquake.logic_tree import LogicTree as OQLogicTree

    from .psha_adapter.hazard_config import HazardConfig

RESOURCES_PATH = Path(__file__).parent.parent / "resources"
SLT_SOURCE_PATH = RESOURCES_PATH / "SRM_JSON"
GMM_JSON_SOURCE_PATH = RESOURCES_PATH / "GMM_JSON"
GMM_SOURCE_PATH = RESOURCES_PATH / "GMM_LTs"


class NshmModel:
    """
    An NshmModel instance represents a complete National Seismic Hazard Model version.
    """

    def __init__(
        self,
        version: str,
        title: str,
        slt_json: Union[str, Path],
        gmm_json: Union[str, Path],
        gmm_xml: Union[str, Path],
        hazard_config: 'HazardConfig',
    ):
        """
        Create a new NshmModel instance.

        NB library users will typically never use this, rather they will obtain a model instance
        using static method: `get_model_version`.
        """
        self.version = version
        self.title = title
        self.hazard_config = hazard_config

        self._slt_json = SLT_SOURCE_PATH / slt_json
        self._gmm_json = GMM_JSON_SOURCE_PATH / gmm_json
        self._gmm_xml = GMM_SOURCE_PATH / gmm_xml
        assert self._slt_json.exists()
        assert self._gmm_json.exists()
        assert self._gmm_xml.exists()

    @property
    def _slt_data(self):
        with open(self._slt_json, 'r') as jsonfile:
            data = json.load(jsonfile)
        return data

    @property
    def _glt_data(self):
        with open(self._gmm_json, 'r') as jsonfile:
            data = json.load(jsonfile)
        return data

    @property
    def source_logic_tree(self) -> SourceLogicTree:
        """
        the source logic tree for this model.

        Returns:
            a source_logic_tree

        """
        data = self._slt_data
        ltv = data.get("logic_tree_version")
        if ltv is None:  # original json is unversioned
            return SourceLogicTree.from_source_logic_tree(SourceLogicTreeV1.from_dict(data))
        elif ltv == 2:
            return SourceLogicTree.from_dict(data)
        raise ValueError("Unsupported logic_tree_version.")

    # def source_logic_tree_nrml(self) -> "OQLogicTree":
    #     """
    #     the Source logic tree for this model as a OpenQuake nrml compatiable type.

    #     Returns:
    #         a source_logic_tree
    #     """
    #     warnings.warn(
    #       "use NshmModel.source_logic_tree().psha_adapter().sources_document() instead", DeprecationWarning
    #        )
    #     return self.psha_adapter(provider=OpenquakeSimplePshaAdapter).sources_document()

    @property
    def gmm_logic_tree_from_xml(self) -> GMCMLogicTree:
        """
        the ground motion logic tree for this model.

        Returns:
            a gmcm_logic_tree

        """
        warnings.warn("use NshmModel.gmm_logic_tree instead", DeprecationWarning)
        return self.psha_adapter(provider=OpenquakeGMCMPshaAdapter).gmcm_logic_tree_from_xml(  # type: ignore
            self._gmm_xml
        )

    @property
    def gmm_logic_tree(self) -> GMCMLogicTree:
        """
        the ground motion logic tree for this model.

        Returns:
            a gmcm_logic_tree

        """
        data = self._glt_data
        return GMCMLogicTree.from_dict(data)

    def gmm_logic_tree_nrml(self) -> "OQLogicTree":
        """
        the ground motion characterisation model (gmcm) logic tree for this model as a OpenQuake nrml compatiable type.

        Returns:
            a gmm_logic_tree.
        """
        doc = NrmlDocument.from_xml_file(self._gmm_xml)
        return doc.logic_trees[0]

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
        model_args_factory = versions.get(version)
        if not model_args_factory:
            raise ValueError(f"{version} is not a valid model version.")

        return cls(**model_args_factory())

    def get_source_branch_sets(self, short_names: Union[List[str], str, None] = None) -> Iterator['SourceBranchSet']:
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
            list_short_names: List[str] = [short_names]
        else:
            list_short_names = short_names if short_names is not None else []

        if not list_short_names:  # User passes either an empty list or None
            for branch_set in self.source_logic_tree.branch_sets:
                yield branch_set
        else:
            # user has passes a list of short_names
            # check all the names are valid:
            for short_name in list_short_names:
                try:
                    for b in filter(lambda item: item.short_name == short_name, self.source_logic_tree.branch_sets):
                        yield (b)
                except StopIteration:
                    raise ValueError("The branch " + short_name + " was not found.")

    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs: Optional[Dict]) -> "PshaAdapterInterface":
        """get a PSHA adapter for this instance.

        Arguments:
            provider: the adapter class
            **kwargs: additional arguments required by the provider class

        Returns:
            a PSHA Adapter instance
        """
        return provider(target=self)
