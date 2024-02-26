# SourceLogicTree configuration format
For use by `SourceLogicTree.from_user_config()`

The config for a `SourceLogicTree` uses the [json file format](https://www.json.org/). It approximates the dict representation of the `SourceLogicTree` dataclass with some simplifications to make it easer to create one manually.

Most of the entries are optional, but without including at least some of them, you will not have a useful `SourceLogicTree`. The basic structure is (comments (`//`) have been included in the example here, but are not compatible with an actual json file):
```
{
    "title": "A sample SRM logic tree definition", 
    "version": "10.1",                             
    "branch_sets": [
        {
            "short_name": "PUY",
            "long_name": "Puysegur",
            "branches": [
                {
                    // A branch name is only necessary if correlations are specified. If so, the name of
                    // every branch (even between branch_sets must be unique).
                    "name": "PUY1",

                    // the weights of the branches in a branch_set must sum to 1.0
                    "weight": 0.2,

                    // Rupture rate scaling (if specified) can be used to scale the rates of all
                    // sources in the branch up or down in a hazard calculation.
                    "rupture_rate_scaling": 1.1,

                    // The values are optional, but can be used to build the structure of the logic
                    // tree. Each entry in the values list is a node and the specific branch on
                    // that node defined by the value of the parameter in question.
                    "values": [
                        {
                            "name": "dm",
                            "long_name": "deformation model",
                            "value": "0.7"
                        },
                        {
                            "name": "bN",
                            "long_name": "bN pair",
                            "value": [
                                0.902,
                                4.6
                            ]
                        }
                    ],

                    // A branch can have multiple sets of earthquake sources.
                    // Each source (rupture definitions and rates) is identified by a nrml_id.
                    // This can be any unique identifier string. Type must be specified and can be
                    // "inversion" or "distributed"; it is not used here, but can be useful to
                    // understand how a set of sources was generated. Each type has additional
                    // parameters that are useful in understanding how the source was generated,
                    // though they are not used here.
                    "sources": [ 
                        {
                            "nrml_id": "ABC",
                            "type": "inversion"
                        },
                        {
                            "nrml_id": "XYZ",
                            "type": "distributed"
                        },
                        {
                            "nrml_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2NjE=",
                            "rupture_rate_scaling": null,
                            "inversion_id": "U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTI5MTM4Mg==",
                            "rupture_set_id": "RmlsZToxMjkwOTg0",
                            "inversion_solution_type": "",
                            "type": "inversion"
                        },
                        {
                            "nrml_id": "RmlsZToxMzA3NTQ=",
                            "rupture_rate_scaling": null,
                            "type": "distributed"
                        }
                    ]
                },
                {
                    "name": "PUY2",
                    "weight": 0.8,
                    "sources": [ 
                        {
                            "nrml_id": "DEF",
                            "type": "inversion"
                        }
                    ]
                }
            ]
        },
        {
            "short_name": "HIK",
            "long_name": "Hikurangi",
            "branches": [
                {
                    "name": "HIK1",
                    "weight": 0.3,
                    "sources": [
                        {
                            "nrml_id": "GHI",
                            "type": "inversion"
                        }
                    ]
                },
                {
                    "name": "HIK2",
                    "weight": 0.2,
                    "sources": [
                        {
                            "nrml_id": "JKL",
                            "type": "inversion"
                        }
                    ]
                },
                {
                    "name": "HIK3",
                    "weight": 0.25,
                    "sources": [
                        {
                            "nrml_id": "MNO",
                            "type": "inversion"
                        }
                    ]
                },
                {
                    "name": "HIK4",
                    "weight": 0.25,
                    "sources": [
                        {
                            "nrml_id": "PQR",
                            "type": "inversion"
                        }
                    ]
                }
            ]
        }
    ],

    // Correlations are used to make branches always be paired with others when forming all
    // combinations of the branch_set branches. Branches are identified by name. The first entry
    // identifies the "primary" branch. The primary branch will only be paired with the other
    // branches in it's list (e.g. "HIK1" will only be combined with "PUY1" not "PUY2"). However,
    // it is possible for the non-primary branches to be combined with more than one branch from
    // the primary list, as shown below. The correlations are not limited to two branches, you can
    // have as many entries as there are branch sets.
    "correlations": [
        ["HIK1", "PUY1"],
        ["HIK2", "PUY2"],
        ["HIK3", "PUY1"],
        ["HIK4", "PUY2"] 
    ]
}  
```