"""Regression tests for Phase 4: PshaAdapterMixin consolidation."""

import pytest

from nzshm_model import get_model_version


def test_psha_adapter_mixin_is_importable():
    """PshaAdapterMixin must be exported from nzshm_model.psha_adapter."""
    from nzshm_model.psha_adapter import PshaAdapterMixin  # noqa: F401


def test_logic_tree_is_psha_adapter_mixin():
    from nzshm_model.psha_adapter import PshaAdapterMixin

    model = get_model_version("NSHM_v1.0.4")
    assert isinstance(model.source_logic_tree, PshaAdapterMixin)


def test_gmcm_logic_tree_is_psha_adapter_mixin():
    from nzshm_model.psha_adapter import PshaAdapterMixin

    model = get_model_version("NSHM_v1.0.4")
    assert isinstance(model.gmm_logic_tree, PshaAdapterMixin)


def test_hazard_config_is_psha_adapter_mixin():
    from nzshm_model.psha_adapter import PshaAdapterMixin

    model = get_model_version("NSHM_v1.0.4")
    assert isinstance(model.hazard_config, PshaAdapterMixin)


def test_nshm_model_is_psha_adapter_mixin():
    from nzshm_model.psha_adapter import PshaAdapterMixin

    model = get_model_version("NSHM_v1.0.4")
    assert isinstance(model, PshaAdapterMixin)
