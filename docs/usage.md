## Get the list of available models

```python3
>>> import nzshm_model as nm
>>> nm.all_model_versions()
['NSHM_v1.0.0', 'NSHM_v1.0.4']
>>>
```

## Work with a specific model

```python3
>>> model = nm.get_model_version("NSHM_v1.0.4")
print(model.title)
>>>
NSHM version 1.0.4, corrected fault geometry
```

## Iterate over the Crustal branches

```python3
>>> for branch_set in model.get_source_branch_sets('CRU'): # NB also allows passing a list of short_names
>>>     for branch in branch_set.branches:
>>>          print(branch_set.long_name, branch.weight, branch.tag)
Crustal 0.0168335471189857 [dmgeodetic, tdFalse, bN[0.823, 2.7], C4.2, s0.66]
...
```

## Inspect a branch

```python3
>>> branch
SourceBranch(weight=0.00286782725429677, values=[dmgeologic, tdTrue, bN[1.089, 4.6], C4.2, s1.41], sources=[InversionSource(nrml_id='SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MzE=', rupture_rate_scaling=None, inversion_id='U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTIwNzc4', rupture_set_id='RmlsZToxMDAwODc=', inversion_solution_type='', type='inversion'), DistributedSource(nrml_id='RmlsZToxMzA3MzE=', rupture_rate_scaling=None, type='distributed')], rupture_rate_scaling=1.0)

```

## OpenQuake Configuration
The `OpenquakeConfig` class is used to define the calculation configuration for an OpenQuake job. It is essentially a wrapper around the OpenQuake `job.ini` file with some helper methods.
```python3
from nzshm_common.location.location import get_locations
from nzshm_model.psha_adapter.openquake import DEFAULT_HAZARD_CONFIG, OpenquakeConfig

# start with the default configuration
oq_config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)
oq_config.set_description("a test OQ job")

# some sites at which to calculate hazard
loc_codes = ["WLG", "AKL", "DUD", "CHC"]
locations = get_locations(loc_codes)
# site conditions
backarc = [0, 1, 0, 0]

# set the site locations and parameters
oq_config.set_sites(locations, backarc=backarc)

# vs30, z1.0, and z2.5 are uniform for all sites
oq_config.set_uniform_site_params(400)

# alternatively, we can  set vs30, z1.0, and z2.5 separately for each site
oq_config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)
# oq_config = OpenquakeConfig()
vs30 = [400, 750, 200, 300]
oq_config.set_sites(locations, vs30=vs30, backarc=backarc)

# set the intensity measure types and levels
imts = ["PGA", "SA(0.5)", "SA(1.0)"]
imtls = [10 ** ((x / 10) - 0.5) for x in range(10)]
oq_config.set_iml(imts, imtls)

# change a calculation parameter
oq_config.set_parameter('erf', 'rupture_mesh_spacing', str(1.0))
```

## OpenQuake Adapters
The adapter classes are used to translate to/from the `nzhsm_model` definition of a hazard model and OpenQuake. OpenQuake files can be read and converted to `nzshm_model` types and and `nzshm_model` types can be written out to OpenQuake compatable input files.
```python3
from pathlib import Path

from nzshm_common.location.location import get_locations
from openquake.hazardlib.site import calculate_z1pt0, calculate_z2pt5

from nzshm_model import get_model_version
from nzshm_model.psha_adapter.openquake import OpenquakeConfigPshaAdapter, OpenquakeModelPshaAdapter

# we need a mapping from the IDs of the sources to a filepath
def source_map(model):
    smap = {}
    for branch in model.source_logic_tree:
        for source in branch.sources:
            nrml_id = source.nrml_id
            smap[nrml_id] = [
                Path(f"path/to/{nrml_id}.xml"),
            ]
    return smap


loc_codes = ["WLG", "AKL", "DUD", "CHC"]
locations = get_locations(loc_codes)
backarc = [0, 1, 0, 0]

model = get_model_version('NSHM_v1.0.4')

model.hazard_config.set_description("a test OQ job")
model.hazard_config.set_sites(locations, backarc=backarc)
model.hazard_config.set_uniform_site_params(400)

imts = ["PGA", "SA(0.5)", "SA(1.0)"]
imtls = [10 ** ((x / 10) - 0.5) for x in range(10)]
model.hazard_config.set_iml(imts, imtls)

# If we just wanted the job.ini and sites.csv file we could use the hazard config adpater
config_adapter = model.hazard_config.psha_adapter(OpenquakeConfigPshaAdapter)
config_adapter.write_config('./tmp/config_test')

# If we want the complete set of OpenQuake input files we use the model adapter
model_adapter = model.psha_adapter(OpenquakeModelPshaAdapter)
model.hazard_config.unset_uniform_site_params()

# site specific parameters
vs30 = [400, 750, 400, 200]
z1pt0 = [calculate_z1pt0(x) for x in vs30]
z2pt5 = [calculate_z2pt5(x) for x in vs30]

model.hazard_config.set_sites(locations, backarc=backarc, vs30=vs30, z1pt0=z1pt0, z2pt5=z2pt5)
model_adapter.write_config('./tmp/cache', './tmp/model_input', source_map(model))
```