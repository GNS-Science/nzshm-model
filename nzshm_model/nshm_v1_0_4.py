#! nshm_v1_0_4.py

import json
from pathlib import Path

import dacite  # for dataclass reconstitution

import nzshm_model.source_logic_tree.SLT_v9p0p0 as slt_config  # NOQA F401

# normalizing with NRML ...
from nzshm_model.nrml.logic_tree import LogicTree, NrmlDocument
from nzshm_model.source_logic_tree.logic_tree import SourceLogicTree

version = 'NSHM_v1.0.4'
title = "NSHM version 1.0.4, corrected fault geometry"

SLT_SOURCE_PATH = Path(__file__).parent / "source_logic_tree" / "nshm_v1.0.4.json"
GMM_SOURCE_PATH = Path(__file__).parent.parent / "GMM_LTs" / "NZ_NSHM_GMM_LT_final_EE.xml"


def source_logic_tree():
    return dacite.from_dict(data_class=SourceLogicTree, data=json.load(open(SLT_SOURCE_PATH)))


def source_logic_tree_nrml():
    slt = source_logic_tree()
    doc = NrmlDocument.from_model_slt(slt)
    return doc.logic_trees[0]


def gmm_logic_tree() -> LogicTree:

    doc = NrmlDocument.from_xml_file(GMM_SOURCE_PATH)
    return doc.logic_trees[0]
