#! v1_0_0.py

import itertools
import json
from pathlib import Path

import dacite  # for dataclass reconstitution

import nzshm_model.source_logic_tree.SLT_v8_gmm_v2_final as slt_config  # NOQA F401
from nzshm_model.source_logic_tree.slt_config import from_config

version = 'NSHM_1.0.4'
title = "NSHM version 1.0.4, corrected fault geometry"

py_slt = Path(__file__).parent / "source_logic_tree" / "SLT_v9p0p0.py"


def source_logic_tree():
    return from_config(py_slt, version, title)
