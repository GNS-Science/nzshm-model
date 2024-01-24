#! nshm_v1_0_0.py

import nzshm_model.logic_tree.source_logic_tree.SLT_v8_gmm_v2_final as slt_config

from .model import NshmModel

model = NshmModel(  # NOQA F401
    version='NSHM_v1.0.0',
    title="Initial version",
    slt_json="nshm_v1.0.0.json",
    gmm_xml="NZ_NSHM_GMM_LT_final_EE_new_names.xml",
    slt_config=slt_config,
)
