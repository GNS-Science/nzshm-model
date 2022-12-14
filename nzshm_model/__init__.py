from . import nshm_1_0_0

# Python package version is different than the NSHM MODEL version !!
__version__ = '0.1.1'

CURRENT_VERSION = "NSHM_1.0.0"

versions = {"NSHM_1.0.0": nshm_1_0_0}


def get_model_version(version_id):
    return versions.get(version_id)
