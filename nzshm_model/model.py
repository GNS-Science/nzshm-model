import json
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

from nzshm_model.psha_adapter import NrmlDocument, OpenquakeSimplePshaAdapter
from nzshm_model.source_logic_tree import SourceLogicTree, SourceLogicTreeV1

if TYPE_CHECKING:
    from nzshm_model.psha_adapter.openquake.logic_tree import LogicTree


RESOURCES_PATH = Path(__file__).parent.parent / "resources"
SLT_SOURCE_PATH = RESOURCES_PATH / "SRM_JSON"
GMM_SOURCE_PATH = RESOURCES_PATH / "GMM_LTs"


class NshmModel:
    def __init__(self, version, title, slt_json, gmm_xml, slt_config):
        self.version = version
        self.title = title
        self.slt_config = slt_config

        self._slt_json = SLT_SOURCE_PATH / slt_json
        self._gmm_xml = GMM_SOURCE_PATH / gmm_xml
        assert self._slt_json.exists()
        assert self._gmm_xml.exists()

    @property
    def _data(self):
        with open(self._slt_json, 'r') as jsonfile:
            data = json.load(jsonfile)
        return data

    def source_logic_tree(self) -> "SourceLogicTree":
        data = self._data
        ltv = data.get("logic_tree_version")
        if ltv is None:  # original json is unversioned
            return SourceLogicTree.from_source_logic_tree(SourceLogicTreeV1.from_dict(data))
        raise ValueError("Unsupported logic_tree_version.")

    def source_logic_tree_nrml(self) -> "LogicTree":
        warnings.warn("use NshmModel.source_logic_tree().psha_adapter().config() instead", DeprecationWarning)
        slt = self.source_logic_tree()
        return slt.psha_adapter(provider=OpenquakeSimplePshaAdapter).config()

    def gmm_logic_tree(self) -> "LogicTree":
        doc = NrmlDocument.from_xml_file(self._gmm_xml)
        return doc.logic_trees[0]
