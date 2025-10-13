"""
This is the top-level package for nzshm_model.

NshmModel is a general representation of an NSHM Logic Tree which includes both **Source** and
**Ground Motion Model (GMM)** logic trees.

## PSHA abstraction and adapters

PSHA applications (such as Openquake, and USGS-PHaz provide methods for calculating hazard based on input models.

PSHA adapter classes convert to/from the internal NSHM source models to the form required by a PSHA tool.
This lets us support different PSHA engines, although currently only an **openquake** adapter
is implemented.

Note that NSHM GMM logic trees use the same serialised form as openquake, so no abstraction is provided.

Todo:
 - about flattening
 - about correlations

Examples:
    >>> import nzshm_model as nm
    >>> nm.all_model_versions()
    ['NSHM_v1.0.0', 'NSHM_v1.0.4']

    >>> model = nm.get_model_version("NSHM_v1.0.4")
    >>> for branch_set in model.get_source_branch_sets('CRU'):
    >>>     for branch in branch_set.branches:
    >>>          print(branch_set.long_name, branch.weight, branch.tag)
    Crustal 0.0168335471189857 [dmgeodetic, tdFalse, bN[0.823, 2.7], C4.2, s0.66]
    ...

Attributes:
    CURRENT_VERSION (str): the version string for the currently published NSHM model.

Functions:
    all_model_versions: lists the available model versions strings
    get_model_version: Get the model instance specified

"""

from . import branch_registry
from .model import NshmModel
from .model_version import CURRENT_VERSION, all_model_versions, get_model_version, versions

# Python package version is different than the NSHM MODEL version !!
__version__ = '0.14.0'
