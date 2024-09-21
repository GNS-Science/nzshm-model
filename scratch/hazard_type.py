"""
can we get a type checker to correctly get the type of model.hazard_config
"""

from nzshm_model import NshmModel, get_model_version
from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig

model = get_model_version('NSHM_v1.0.4')
model.hazard_config  # Any
model.gmm_logic_tree  # GMCMLogicTree

slt = model.source_logic_tree
gmcm = model.gmm_logic_tree

model2 = NshmModel('', '', slt, gmcm, OpenquakeConfig())
reveal_type(model2.hazard_config)  # OpenquakeConfig (acomplished by using HazardConfigType and Generic)
model2.hazard_config

model_from_files = NshmModel.from_files(
    '',
    '',
    '/Users/dicaprio/NSHM/DEV/LIB/nzshm-model/resources/SRM_JSON/nshm_v1.0.4_v2.json',
    '/Users/dicaprio/NSHM/DEV/LIB/nzshm-model/resources/GMM_JSON/gmcm_nshm_v1.0.4.json',
    OpenquakeConfig(),
)

model_from_files.gmm_logic_tree
reveal_type(
    model_from_files.hazard_config
)  # Any, even when explicitly creating an OpenquakeConfig object in the classmethod from_files()

# something about using a classmethod kills the ability of the type checker to get the type of omdel.hazard_config

from typing import TypeVar, Generic

AType = TypeVar("AType", bound="A")

class A:

    def a_method(self):
        print("a_method")

class B(A):

    def b_method(self):
        print("b_method")

class M(Generic[AType]):

    def __init__(self, a: AType):
        self.a = a

    @classmethod
    def constructor(cls, a: AType) -> 'M[AType]':
        return cls(a)

b = B()
m1 = M(b)
reveal_type(m1.a)
m2 = M.constructor(b)
reveal_type(m2.a)         