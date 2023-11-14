from . import nshm_v1_0_0, nshm_v1_0_4

# Python package version is different than the NSHM MODEL version !!
__version__ = '0.3.1'

CURRENT_VERSION = "NSHM_v1.0.0"

versions = {
    "NSHM_v1.0.0": nshm_v1_0_0,
    "NSHM_v1.0.4": nshm_v1_0_4,
}


def get_model_version(version_id):
    return versions.get(version_id)
