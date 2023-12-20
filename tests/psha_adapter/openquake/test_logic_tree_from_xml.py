#! python test_logic_tree.py

from pathlib import Path, PurePath

import pytest

from nzshm_model.psha_adapter.openquake import NrmlDocument
from nzshm_model.psha_adapter.openquake.uncertainty_models import _strip_whitespace

FIXTURE_PATH = Path(__file__).parent / "fixtures"


def test_nrml_gmm_logic_tree():
    gmm_logic_tree_path = FIXTURE_PATH / "TEST_GMM_LT.xml"
    doc = NrmlDocument.from_xml_file(gmm_logic_tree_path)

    logic_trees = list(doc.logic_trees)
    assert len(logic_trees) == 1

    crustal_branch = logic_trees[0].branch_sets[0]
    assert crustal_branch.applyToTectonicRegionType == "Active Shallow Crust"
    assert crustal_branch.branchSetID == "bs_crust"

    assert len(crustal_branch.branches) == 1

    # branch uncertainty weight
    assert doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_weight == pytest.approx(0.117000)

    # branch uncertainty models
    assert "Stafford2022" in doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_models[0].text
    assert doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_models[0].gmpe_name == "[Stafford2022]"
    assert doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_models[0].arguments[0] == "mu_branch = \"Upper\""


def test_nrml_gmm_logic_tree_reverse_tree():
    gmm_logic_tree_path = FIXTURE_PATH / "TEST_GMM_LT.xml"
    doc = NrmlDocument.from_xml_file(gmm_logic_tree_path)

    assert (
        doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_models[0].parent
        is doc.logic_trees[0].branch_sets[0].branches[0]
    )

    assert doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_models[0].parent.branchID == "STF22_upper"


def test_nrml_gmm_logic_tree_paths():
    gmm_logic_tree_path = FIXTURE_PATH / "TEST_GMM_LT.xml"
    doc = NrmlDocument.from_xml_file(gmm_logic_tree_path)

    # LogicTreeBranch path
    assert doc.logic_trees[0].branch_sets[0].branches[0].path() == PurePath("lt1", "bs_crust", "STF22_upper")
    assert doc.logic_trees[0].branch_sets[1].branches[0].path() == PurePath("lt1", "bs_slab", "Kuehn2020SS_GLO_lower")

    # uncertainty model path
    assert doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_models[0].path() == PurePath(
        "lt1",
        "bs_crust",
        "STF22_upper",
        '[Stafford2022]mu_branch="Upper"',
    )

    assert doc.logic_trees[0].branch_sets[1].branches[0].uncertainty_models[0].path() == PurePath(
        "lt1",
        "bs_slab",
        "Kuehn2020SS_GLO_lower",
        '[KuehnEtAl2020SSlab]region="GLO"' 'sigma_mu_epsilon=-1.28155',
    )


SRC_TEST_DATA = [
    pytest.param(
        "TEST_SRC_LT_example_1.xml",
        "Combined",
        "BS-NONCE1",
        "CR_3km",
        1.0,
        "SW52ZXJzaW9uU29sdXRpb246MTAwMTkx-ruptures.xml\t\n"
        "            SW52ZXJzaW9uU29sdXRpb246MTAwMTkx-ruptures_sections.xml",
        id='example_1',
    ),
    pytest.param(
        "TEST_SRC_LT_example_2.xml",
        "Combined",
        "BS-NONCE1",
        "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEwNjQ2NA==|RmlsZToxMDY1MzM=|"
        "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEwNjQ5Mg==|RmlsZToxMDY1NTQ=|SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEwNjUwNg==|"
        "RmlsZToxMDY1NTM=",
        0.0833333,
        "U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTA2MzYw-ruptures.xml\t"
        "U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTA2MzYw-ruptures_sections.xml\t"
        "Floor_AddoptiEEPAScomb-INT_hiktcrp_b1.10_N17.18.xml\t"
        "U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTA2NDEw-ruptures.xml\t"
        "U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTA2NDEw-ruptures_sections.xml\t"
        "Floor_AddoptiEEPAScomb-INT_puy_b0.85_N4.36.xml\t"
        "U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTA2NDE4-ruptures_sections.xml\t"
        "U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTA2NDE4-ruptures.xml\tFloor_AddoptiEEPAScomb-CRU_plyadj_b0.85_N4.36.xml",
        id='example_2',
    ),
]


@pytest.mark.parametrize(
    "fixture_file, logic_tree_id, branch_set_id, branch_id, uncertainty_weight, uncertainty_model", SRC_TEST_DATA
)
def test_nrml_srm_logic_tree(
    fixture_file, logic_tree_id, branch_set_id, branch_id, uncertainty_weight, uncertainty_model
):

    srm_logic_tree_path = FIXTURE_PATH / fixture_file
    doc = NrmlDocument.from_xml_file(srm_logic_tree_path)

    # logic tree 0
    assert len(doc.logic_trees) == 1
    assert doc.logic_trees[0].logicTreeID == logic_tree_id

    # branch_set 0
    assert len(doc.logic_trees[0].branch_sets) == 1
    assert doc.logic_trees[0].branch_sets[0].branchSetID == branch_set_id

    # branch 0
    assert len(doc.logic_trees[0].branch_sets[0].branches) == 1
    assert doc.logic_trees[0].branch_sets[0].branches[0].branchID == branch_id

    # branch 0 uncertainty weight
    assert doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_weight == pytest.approx(uncertainty_weight)

    # branch 0 uncertainty models
    assert uncertainty_model in doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_models[0].text


@pytest.mark.parametrize(
    "fixture_file, logic_tree_id, branch_set_id, branch_id, uncertainty_weight, uncertainty_model", SRC_TEST_DATA
)
def test_nrml_srm_logic_tree_parents(
    fixture_file, logic_tree_id, branch_set_id, branch_id, uncertainty_weight, uncertainty_model
):

    srm_logic_tree_path = FIXTURE_PATH / fixture_file
    doc = NrmlDocument.from_xml_file(srm_logic_tree_path)

    # parental reference
    assert (
        doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_models[0].parent
        is doc.logic_trees[0].branch_sets[0].branches[0]
    )

    assert doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_models[0].parent.branchID == branch_id


@pytest.mark.parametrize(
    "fixture_file, logic_tree_id, branch_set_id, branch_id, uncertainty_weight, uncertainty_model", SRC_TEST_DATA
)
def test_nrml_srm_logic_tree_path(
    fixture_file, logic_tree_id, branch_set_id, branch_id, uncertainty_weight, uncertainty_model
):

    srm_logic_tree_path = FIXTURE_PATH / fixture_file
    doc = NrmlDocument.from_xml_file(srm_logic_tree_path)

    assert doc.logic_trees[0].branch_sets[0].branches[0].path() == PurePath(logic_tree_id, branch_set_id, branch_id)

    assert doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_models[0].path() == PurePath(
        _strip_whitespace(logic_tree_id),
        _strip_whitespace(branch_set_id),
        _strip_whitespace(branch_id),
        _strip_whitespace(uncertainty_model),
    )
