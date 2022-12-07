class SourceLogicTreeLeaf:
    """
    str: fault_system hikurangi/hik, puysegur/puy, crustal/cru, itraslab/slab
    tuple: b_n_pair
    float: c (area-magnitude scaling)
    float: s (moment rate scaling)
    str deformation_model: hik locked, geodetic, geologic
    bool: time_dependence
    float: weight
    str: nrml_id_inv
    str: nrml_id_bg
    """

class SourceLogicTreeCorrelation:
    """
    List[SourceLogicTreeBranch]: branch_sets
    """

class BranchLevel:
    """
    str: name
    str: long_name
    List[Branch]: branches
    """

class Branch:
    """
    any: value
    float: weight
    """


class FaultSystemLogicTree:
    """
    List[BranchLevel]: branch_levels
    """

class SourceLogicTree:
    """
    List[SourceLogicTreeCorrelation]: correlations
    List[FaultSystemLogicTree]: 
    str: weight_master (SourceLogicTreeBranch.fault_system to use for weighting when logic trees are correlated)
    """