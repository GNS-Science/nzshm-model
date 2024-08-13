#! nshm_v1_0_4.py
from typing import Any, Dict

from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig
from nzshm_model.psha_adapter.openquake.hazard_config_compat import DEFAULT_HAZARD_CONFIG


def model_args_factory() -> Dict[str, Any]:
    return dict(
        version='NSHM_v1.0.4',
        title="NSHM version 1.0.4, corrected fault geometry",
        slt_json="nshm_v1.0.4_v2.json",
        gmm_json="gmcm_nshm_v1.0.4.json",
        gmm_xml="NZ_NSHM_GMM_LT_final_EE_new_names.xml",
        hazard_config=OpenquakeConfig(DEFAULT_HAZARD_CONFIG),
    )
