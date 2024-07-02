from pathlib import Path

from nzshm_model.logic_tree import GMCMBranch, GMCMLogicTree

gmcm_json_filepath = Path(__file__).parent / 'fixtures' / 'gmcm_logic_tree_example.json'

gmcm_logic_tree = GMCMLogicTree.from_json(gmcm_json_filepath)


def test_filter_trt():
    gsim_args = {'epistemic': 'Central', 'modified_sigma': 'true'}
    # assert (
    #     len(
    #         [
    #             filt_branch
    #             for filt_branch in filter(
    #                 lambda obj: obj.branch_set.tectonic_region_type == 'Active Shallow Crust', gmcm_logic_tree
    #             )
    #         ]
    #     )
    #     == 21
    # )
    assert (
        len([filt_branch for filt_branch in filter(lambda obj: obj.gsim_name == 'Atkinson2022SInter', gmcm_logic_tree)])
        == 3
    )
    assert len([filt_branch for filt_branch in filter(lambda obj: obj.gsim_args == gsim_args, gmcm_logic_tree)]) == 3


def test_build_gmcmlt_from_filtered_gmcmlt():
    flt = (filt_branch for filt_branch in filter(lambda obj: obj.gsim_name == 'Atkinson2022SInter', gmcm_logic_tree))
    glt = GMCMLogicTree.from_branches(flt)
    print(glt)
    assert len(glt.branch_sets) == 1
    assert len(glt.branch_sets[0].branches) == 3
    assert (
        type(glt.branch_sets[0].branches[0]) is GMCMBranch
    )  # isinstance() not used to avoid true for inherited classes
