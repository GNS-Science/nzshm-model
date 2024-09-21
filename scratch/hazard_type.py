from nzshm_model import get_model_version, NshmModel
from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig

model = get_model_version('NSHM_v1.0.4')
# model.hazard_config.get_iml()
model.hazard_config.get_iml()
model.gmm_logic_tree

oqconfig = OpenquakeConfig()
oqconfig.get_iml()

print(help(model.hazard_config))

slt = model.source_logic_tree
gmcm = model.gmm_logic_tree

model2 = NshmModel('', '', slt, gmcm, OpenquakeConfig())
model2.hazard_config

