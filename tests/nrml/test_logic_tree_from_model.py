#! python test_logic_tree.py

from pathlib import Path, PurePath

import pytest

import nzshm_model

MODEL = nzshm_model.get_model_version('NSHM_v1.0.4')
FIXTURE_PATH = Path(__file__).parent / "fixtures"


def test_gmm_logic_tree():

    gmm_logic_tree = MODEL.gmm_logic_tree()

    assert len(gmm_logic_tree.branch_sets) == 3

    # branch set attributes
    assert gmm_logic_tree.branch_sets[0].applyToTectonicRegionType == "Active Shallow Crust"
    assert gmm_logic_tree.branch_sets[0].branchSetID == "bs_crust"
    assert len(gmm_logic_tree.branch_sets[0].branches) == 21

    # branch attributes
    assert gmm_logic_tree.branch_sets[0].branches[0].uncertainty_weight == pytest.approx(0.117000)
    assert gmm_logic_tree.branch_sets[0].branches[0].branchID == "STF22_upper"
    assert gmm_logic_tree.branch_sets[0].branches[0].path() == PurePath("STF22_upper") / "bs_crust" / 'lt1'

    # uncertainty model attributes
    assert "Stafford2022" in gmm_logic_tree.branch_sets[0].branches[0].uncertainty_models[0].text
    assert gmm_logic_tree.branch_sets[0].branches[0].uncertainty_models[0].gmpe_name == "[Stafford2022]"
    assert gmm_logic_tree.branch_sets[0].branches[0].uncertainty_models[0].arguments[0] == "mu_branch = \"Upper\""


def test_source_logic_tree():

    src_logic_tree = MODEL.source_logic_tree_nrml()

    assert len(src_logic_tree.branch_sets) == 4

    # branch set attributes
    assert src_logic_tree.branch_sets[0].applyToTectonicRegionType == ""
    assert src_logic_tree.branch_sets[0].branchSetID == "PUY"
    assert src_logic_tree.branch_sets[3].branchSetID == "SLAB"

    assert len(src_logic_tree.branch_sets[0].branches) == 3

    # branch attributes
    assert src_logic_tree.branch_sets[0].branches[0].branchID == "[dm0.7, bN[0.902, 4.6], C4.0, s0.28]"
    assert src_logic_tree.branch_sets[0].branches[0].uncertainty_weight == pytest.approx(0.210000)
    assert (
        src_logic_tree.branch_sets[0].branches[0].path()
        == PurePath("[dm0.7, bN[0.902, 4.6], C4.0, s0.28]") / "PUY" / 'NSHM_v1.0.4'
    )


def test_source_logic_tree_uncertainty_PUY():
    # uncertainty model attributes (SourceUncertaintyModel)
    # NB for crustal, the first is the ltb.onfault_nrml_id
    #    the 2nd is ltb.distributed_nrml_id

    src_logic_tree = MODEL.source_logic_tree_nrml()
    BSID = 0

    assert src_logic_tree.branch_sets[BSID].branchSetID == "PUY"
    assert src_logic_tree.branch_sets[BSID].branches[0].path() == PurePath(
        '[dm0.7, bN[0.902, 4.6], C4.0, s0.28]', 'PUY', 'NSHM_v1.0.4'
    )

    assert len(src_logic_tree.branch_sets[BSID].branches[0].uncertainty_models) == 2

    # ==> NZSHM22_ScaledInversionSolution-QXV0b21hdGlvblRhc2s6MTMyNzM5Mw==_nrml.zip
    # U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTI5MTM3OA__-ruptures.hdf5
    # U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTI5MTM3OA__-ruptures_sections.xml
    # U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTI5MTM3OA__-ruptures.xml
    # http://simple-toshi-ui.s3-website-ap-southeast-2.amazonaws.com/InversionSolutionNrml/SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2NTc=
    assert (
        src_logic_tree.branch_sets[BSID].branches[0].uncertainty_models[0] == "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2NTc="
    )

    # ==> npFloor_MULTOT1346GruEEPAScomb-INT_puy_b0.90_N0.73.xml
    # http://simple-toshi-ui.s3-website-ap-southeast-2.amazonaws.com/FileDetail/RmlsZToxMzA3NTM=
    assert src_logic_tree.branch_sets[BSID].branches[0].uncertainty_models[1] == "RmlsZToxMzA3NTM="


def test_source_logic_tree_uncertainty_SLAB():
    # uncertainty model attributes (SourceUncertaintyModel)
    # NB for slab we have just a distributed model

    src_logic_tree = MODEL.source_logic_tree_nrml()
    BSID = 3

    assert src_logic_tree.branch_sets[BSID].branchSetID == "SLAB"
    assert src_logic_tree.branch_sets[BSID].branches[0].path() == PurePath('[runiform, d1]', 'SLAB', 'NSHM_v1.0.4')

    assert len(src_logic_tree.branch_sets[BSID].branches[0].uncertainty_models) == 1

    # ==> slab-uniform-1depth-rates.xml.zip
    # slab-uniform-1depth-rates.xml (8.5 MB)
    # http://simple-toshi-ui.s3-website-ap-southeast-2.amazonaws.com/FileDetail/RmlsZToxMjEwMzM=
    assert src_logic_tree.branch_sets[BSID].branches[0].uncertainty_models[0] == "RmlsZToxMjEwMzM="


def test_source_logic_tree_uncertainty_CRU():
    # uncertainty model attributes (SourceUncertaintyModel)

    src_logic_tree = MODEL.source_logic_tree_nrml()
    BSID = 2
    assert src_logic_tree.branch_sets[BSID].branchSetID == "CRU"
    assert src_logic_tree.branch_sets[BSID].branches[0].path() == PurePath(
        '[dmgeodetic, tdFalse, bN[0.823, 2.7], C4.2, s0.66]/CRU/NSHM_v1.0.4'
    )
    assert len(src_logic_tree.branch_sets[BSID].branches[0].uncertainty_models) == 2

    # ==> NZSHM22_ScaledInversionSolution-QXV0b21hdGlvblRhc2s6MTEzMTQz_nrml.zip
    # http://simple-toshi-ui.s3-website-ap-southeast-2.amazonaws.com/Find/SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MDE=
    assert (
        src_logic_tree.branch_sets[BSID].branches[0].uncertainty_models[0] == "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MDE="
    )

    # ==> npFloor_MULTOT1346GruEEPAScomb-CRU_plyadj_ratestapered_b0.82_N2.57.xml.zip
    # http://simple-toshi-ui.s3-website-ap-southeast-2.amazonaws.com/Find/RmlsZToxMzA3MDc=
    assert src_logic_tree.branch_sets[BSID].branches[0].uncertainty_models[1] == "RmlsZToxMzA3MDc="
