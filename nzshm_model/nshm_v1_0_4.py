#! nshm_v1_0_4.py

# Is this only used for the correlations ??
import nzshm_model.logic_tree.source_logic_tree.SLT_v9p0p0 as slt_config

from .model import NshmModel

model = NshmModel(  # NOQA F401
    version='NSHM_v1.0.4',
    title="NSHM version 1.0.4, corrected fault geometry",
    slt_json="nshm_v1.0.4.json",
    gmm_xml="NZ_NSHM_GMM_LT_final_EE_new_names.xml",
    slt_config=slt_config,
)
