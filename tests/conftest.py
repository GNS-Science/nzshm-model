import pytest

from nzshm_model import get_model_version

CURRENT_VERSION = "NSHM_v1.0.4"


@pytest.fixture(scope='function')
def current_version():
    return CURRENT_VERSION


@pytest.fixture
def current_model(current_version):
    return get_model_version(current_version)
