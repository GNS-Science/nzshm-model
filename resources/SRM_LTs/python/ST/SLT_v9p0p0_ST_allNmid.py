gt_description = "Source Logic Tree v9.0.0"

logic_tree_permutations = [
    [
        {
            "tag": "Final SLT for TAG Workshop - Hik fix, Cru fix, Puy fix",
            "weight": 1.0,
            "permute": [
                {
                    "group": "Hik",
                    "nrlz": 12,
                    "members": [
                        {
                            "tag": "Hik TL, N16.5, b0.95, C4, s1",
                            "weight": 1.0,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2MDU=",
                            "bg_id": "RmlsZToxMzA3MzQ=",
                        },
                    ],
                },
                {
                    "group": "PUY",
                    "nrlz": 12,
                    "members": [
                        {
                            "tag": "Puy 0.7, N4.6, b0.902, C4, s1",
                            "weight": 1.0,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2NjE=",
                            "bg_id": "RmlsZToxMzA3NTQ=",
                        },
                    ],
                },
                {
                    "group": "CRU",
                    "nrlz": 21,
                    "members": [
                        {
                            "tag": "geologic, TI, N3.4, b0.959 C4.2 s1",
                            "weight": 1.0,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0NzY=",
                            "bg_id": "RmlsZToxMzA3MTk=",
                        },
                    ],
                },
                {
                    "group": "SLAB",
                    "nrlz": 12,
                    "members": [
                        {"tag": "slab-uniform-1depth-rates", "weight": 1.0, "inv_id": "", "bg_id": "RmlsZToxMjEwMzM="}
                    ],
                },
            ],
        }
    ]
]
