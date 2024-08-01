import pytest

from nzshm_model import get_model_version
from nzshm_model.logic_tree.gmcm_logic_tree import GMCMBranch, GMCMBranchSet
from nzshm_model.logic_tree.source_logic_tree import SourceBranch, SourceBranchSet
from nzshm_model.logic_tree.source_logic_tree.logic_tree import DistributedSource


def test_source_trts():
    b1 = SourceBranch(
        tectonic_region_types=("a", "b"), branch_id="1", weight=0.5, sources=[DistributedSource(nrml_id="ABC")]
    )
    b2 = SourceBranch(
        tectonic_region_types=("a", "b"), branch_id="2", weight=0.5, sources=[DistributedSource(nrml_id="DEF")]
    )
    b3 = SourceBranch(
        tectonic_region_types=("c", "b"), branch_id="2", weight=0.5, sources=[DistributedSource(nrml_id="DEF")]
    )

    with pytest.raises(ValueError):
        sbs = SourceBranchSet(branches=(b1, b2, b3))

    sbs = SourceBranchSet(branches=(b1, b2))
    assert sbs.tectonic_region_types == ("a", "b")

    with pytest.raises(AttributeError):
        sbs.tectonic_region_types = ("c", "d")


def test_gmcm_trts():
    b1 = GMCMBranch(tectonic_region_type="a", branch_id="1", weight=0.5)
    b2 = GMCMBranch(tectonic_region_type="a", branch_id="2", weight=0.5)
    b3 = GMCMBranch(tectonic_region_type="b", branch_id="2", weight=0.5)

    with pytest.raises(ValueError):
        gbs = GMCMBranchSet(branches=(b1, b2, b3))

    gbs = GMCMBranchSet(branches=(b1, b2))
    assert gbs.tectonic_region_type == "a"

    with pytest.raises(AttributeError):
        gbs.tectonic_region_type = "c"


def test_model_trts():
    model = get_model_version('NSHM_v1.0.4')

    glt = model.gmm_logic_tree
    trts = ["Active Shallow Crust", "Subduction Interface", "Subduction Intraslab"]
    for branch_set, trt in zip(glt.branch_sets, trts):
        assert branch_set.tectonic_region_type == trt
        assert branch_set.branches[0].tectonic_region_type == trt

    slt = model.source_logic_tree
    trts = ["Subduction Interface", "Subduction Interface", "Active Shallow Crust", "Subduction Intraslab"]
    for branch_set, trt in zip(slt.branch_sets, trts):
        assert branch_set.tectonic_region_types == (trt,)
        assert branch_set.branches[0].tectonic_region_types == (trt,)
