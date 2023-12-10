"""
test migration from slt v1 to v2
"""
import pytest

import nzshm_model


## three example filter functions
def unscaled_filter_str(obj):
    return "s1.0" in [str(v) for v in obj.values]


def unscaled_filter(obj):
    for v in obj.values:
        if v.name == 's' and v.value == 1.0:  # moment rate scaling
            return True
    return False


def geodetic_filter(obj):
    for v in obj.values:
        if v.long_name == 'deformation model' and v.value == "geodetic":
            return True


@pytest.fixture(scope='module')
def full_slt():
    yield nzshm_model.get_model_version('NSHM_v1.0.4').source_logic_tree()


def test_filter_fn_on_logic_tree_branches(full_slt):
    # functional style
    assert len([slt for slt in filter(lambda obj: obj.fslt.short_name == 'HIK', full_slt)]) == 9
    assert len([slt for slt in filter(unscaled_filter_str, full_slt)]) == 16
    assert len([slt for slt in filter(unscaled_filter, full_slt)]) == 16
    assert len([slt for slt in filter(geodetic_filter, full_slt)]) == 18
    assert len([slt for slt in filter(unscaled_filter, filter(geodetic_filter, full_slt))]) == 6


def test_list_comprehension_filtering_logic_tree_branches(full_slt):
    # old-skool pythonic style
    assert len([slt for slt in full_slt if slt.fslt.short_name == "HIK"]) == 9
    assert len([slt for slt in full_slt if unscaled_filter_str(slt)]) == 16
    assert len([slt for slt in full_slt if unscaled_filter(slt)]) == 16
    assert len([slt for slt in full_slt if geodetic_filter(slt)]) == 18
    assert len([slt for slt in full_slt if unscaled_filter(slt) and geodetic_filter(slt)]) == 6


def test_generator_filtering_logic_tree_branches(full_slt):
    # most memory efficient & pythonic
    assert sum((1 for slt in full_slt if slt.fslt.short_name == "HIK")) == 9
    assert sum(1 for slt in full_slt if unscaled_filter_str(slt)) == 16
    assert sum(1 for slt in full_slt if unscaled_filter(slt)) == 16
    assert sum(1 for slt in full_slt if geodetic_filter(slt)) == 18
    assert sum(1 for slt in full_slt if unscaled_filter(slt) and geodetic_filter(slt)) == 6
