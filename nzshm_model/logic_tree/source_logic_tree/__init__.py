"""
The source_logic_tree package provides dataclasses that define the
Source Logic Tree dataclasses.
"""

from .branch_attribute import BranchAttributeSpec, BranchAttributeValue
from .logic_tree import InversionSource, SourceBranch, SourceBranchSet, SourceLogicTree
from .version1.logic_tree import SourceLogicTree as SourceLogicTreeV1
from .version1.logic_tree import SourceLogicTreeCorrelation
