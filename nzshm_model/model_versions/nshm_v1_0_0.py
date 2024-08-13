#! nshm_v1_0_0.py
from typing import Any, Dict

from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig
from nzshm_model.psha_adapter.openquake.hazard_config_compat import DEFAULT_HAZARD_CONFIG


def model_args_factory() -> Dict[str, Any]:
    return dict(
        version='NSHM_v1.0.0',
        title="Initial version",
        slt_json="nshm_v1.0.0.json",
        gmm_json="gmcm_nshm_v1.0.0.json",
        gmm_xml="NZ_NSHM_GMM_LT_final_EE_new_names.xml",
        hazard_config=OpenquakeConfig(DEFAULT_HAZARD_CONFIG),
    )
