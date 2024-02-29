# GMCMLogicTree configuration format
For use by `GMCMLogicTree.from_user_config()`

The config for a `GMCMLogicTree` uses the [json file format](https://www.json.org/). It approximates the dict representation of the `SourceLogicTree` dataclass with some simplifications to make it easer to create one manually.

Most of the entries are optional, but without including at least some of them, you will not have a useful `GMCMLogicTree`. Comments (`//`) have been included in the example here, but are not compatible with an actual json file.

The branch set `short_name` and branch `name` are used to define correlations. Therefore, if correlations are specified each branch must have a unique `branch_set.short_name:branch.name` combination. Otherwise, branch set `short_name` and branch `name` are optional, as is branch_set `long_name`.
```

    "version": "ten.2",
    "title": "gmcm logic tree number 10",
    "branch_sets": [
        {
            "short_name": "asc",
            "long_name": "active_shallow_crust",

            // tectonic_region_type may be used by the hazard engine to apply the gsim to the correct TRT
            "tectonic_region_type": "Active Shallow Crust",
            "branches": [
                {
                    // gsim_name and gsim_args are indented to be used by the hazard engine to specify the ground motion model for the branch
                    "gsim_name": "Stafford2022",
                    "gsim_args": {
                        "mu_branch": "Upper"
                    },
                    "weight": 0.3
                },
                {
                    "gsim_name": "Stafford2022",
                    "gsim_args": {
                        "mu_branch": "Central"
                    },
                    "weight": 0.4
                },
                {
                    "gsim_name": "Stafford2022",
                    "gsim_args": {
                        "mu_branch": "Lower"
                    },
                    "weight": 0.3
                }
            ]
        },
        {
            "tectonic_region_type": "Subduction Interface",
            "branches": [
                {
                    "gsim_name": "Atkinson2022SInter",
                    "gsim_args": {
                        "epistemic": "Upper",
                        "modified_sigma": "true"
                    },
                    "weight": 0.3
                },
                {
                    "gsim_name": "Atkinson2022SInter",
                    "gsim_args": {
                        "epistemic": "Central",
                        "modified_sigma": "true"
                    },
                    "weight": 0.4
                },
                {
                    "gsim_name": "Atkinson2022SInter",
                    "gsim_args": {
                        "epistemic": "Lower",
                        "modified_sigma": "true"
                    },
                    "weight": 0.3
                }
            ]
        },
        {
            "tectonic_region_type": "Subduction Intraslab",
            "branches": [
                {
                    "gsim_name": "NZNSHM2022_ParkerEtAl2020SSlab",
                    "gsim_args": {
                        "sigma_mu_epsilon": "0.0",
                        "modified_sigma": "true"
                    },
                    "weight": 1.0
                }
            ]
        }
    ]
}
```