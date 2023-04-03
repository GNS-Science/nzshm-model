#! nshm_v1_0_4.py

import json
from pathlib import Path

import dacite  # for dataclass reconstitution

import nzshm_model.source_logic_tree.SLT_v9p0p0 as slt_config  # NOQA F401
from nzshm_model.source_logic_tree.logic_tree import SourceLogicTree

version = 'NSHM_1.0.4'
title = "NSHM version 1.0.4, corrected fault geometry"

json_slt = Path(__file__).parent / "source_logic_tree" / "SLT_v9p0p0.json"


def source_logic_tree():
    return dacite.from_dict(data_class=SourceLogicTree, data=json.load(open(json_slt)))
