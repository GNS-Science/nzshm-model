"""
The logic_tree package provides dataclasses that define the different types of LogicTree
and Logic Tree Branches

Classes:
    LogicTree: an Abstract Base Class for LogicTrees
    SourceLogicTree: dataclass for source logic trees
    SourceLogicTreeV1: (Deprecated)
    GMCMLogicTree: dataclass for Ground Motion Model logic trees
    SourceBranch: dataclass for individual source branches
    SourceBranchSet: dataclass for grouping source branches

"""

from .branch import CompositeBranch
from .correlation import Correlation, LogicTreeCorrelations
from .gmcm_logic_tree import GMCMBranch, GMCMBranchSet, GMCMLogicTree
from .source_logic_tree import InversionSource, SourceBranch, SourceBranchSet, SourceLogicTree, SourceLogicTreeV1
