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
                            "tag": "Hik TL, N16.5, b0.95, C4, s1.58",
                            "weight": 1.0,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2MDM=",
                            "bg_id": "RmlsZToxMzA3MzY=",
                        },
                    ],
                },
                {
                    "group": "PUY",
                    "nrlz": 12,
                    "members": [
                        {
                            "tag": "Puy 0.7, N4.6, b0.902, C4, s1.72",
                            "weight": 1.0,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2NjY=",
                            "bg_id": "RmlsZToxMzA3NTU=",
                        },
                    ],
                },
                {
                    "group": "CRU",
                    "nrlz": 21,
                    "members": [
                        {
                            "tag": "geologic, TI, N3.4, b0.959 C4.2 s1.41",
                            "weight": 1.0,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0Njc=",
                            "bg_id": "RmlsZToxMzA3MjI=",
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
