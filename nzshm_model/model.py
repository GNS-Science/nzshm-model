import json
from pathlib import Path

import dacite

from nzshm_model.nrml.logic_tree import LogicTree, NrmlDocument
from nzshm_model.source_logic_tree.logic_tree import SourceLogicTree

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

    def source_logic_tree(self) -> SourceLogicTree:
        return dacite.from_dict(data_class=SourceLogicTree, data=json.load(open(self._slt_json)))

    def source_logic_tree_nrml(self) -> LogicTree:
        slt = self.source_logic_tree()
        doc = NrmlDocument.from_model_slt(slt)
        return doc.logic_trees[0]

    def gmm_logic_tree(self) -> LogicTree:
        doc = NrmlDocument.from_xml_file(self._gmm_xml)
        return doc.logic_trees[0]
