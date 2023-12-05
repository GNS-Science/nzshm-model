#! python test_logic_tree.py

import dataclasses
import itertools
from pathlib import Path

import pytest

from nzshm_model.source_logic_tree.version2 import (
    # Branch,
    # BranchAttributeSpec,
    # BranchAttributeValue,
    # CompositeBranch,
    # FaultSystemLogicTree,
    # FlattenedSourceLogicTree,
    SourceLogicTree,
    # SourceLogicTreeCorrelation,
)


def test_source_tree_from_json():
    config = Path(__file__).parent / 'fixtures' / 'source_logic_tree_sample_1.json'
    slt = SourceLogicTree.from_json(config)
    # slt_spec = slt.derive_spec()    

