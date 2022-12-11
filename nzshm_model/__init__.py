from . import nshm_1_0_0

CURRENT_VERSION = "NSHM_1.0.0"

versions = [dict(id="NSHM_1.0.0", title="Initial Release", model=nshm_1_0_0)]

def get_model_version(version_id):
    for model_version in versions:
        if model_version['id'] == version_id:
            return model_version


