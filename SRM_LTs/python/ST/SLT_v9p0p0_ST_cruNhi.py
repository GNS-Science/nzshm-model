gt_description = "Source Logic Tree v9.0.0"

src_correlations = {
    "dropped_group": "PUY",
    "correlations": [
        [
            {"group": "Hik", "tag": "Hik TL, N16.5, b0.95, C4, s0.42"},
            {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s0.28"},
        ],
        [
            {"group": "Hik", "tag": "Hik TL, N16.5, b0.95, C4, s1"},
            {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s1"},
        ],
        [
            {"group": "Hik", "tag": "Hik TL, N16.5, b0.95, C4, s1.58"},
            {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s1.72"},
        ],
        [
            {"group": "Hik", "tag": "Hik TL, N21.5, b1.097, C4, s0.42"},
            {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s0.28"},
        ],
        [
            {"group": "Hik", "tag": "Hik TL, N21.5, b1.097, C4, s1"},
            {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s1"},
        ],
        [
            {"group": "Hik", "tag": "Hik TL, N21.5, b1.097, C4, s1.58"},
            {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s1.72"},
        ],
        [
            {"group": "Hik", "tag": "Hik TL, N27.9, b1.241, C4, s0.42"},
            {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s0.28"},
        ],
        [
            {"group": "Hik", "tag": "Hik TL, N27.9, b1.241, C4, s1"},
            {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s1"},
        ],
        [
            {"group": "Hik", "tag": "Hik TL, N27.9, b1.241, C4, s1.58"},
            {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s1.72"},
        ],
    ],
}

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
                            "tag": "Hik TL, N16.5, b0.95, C4, s0.42",
                            "weight": 0.147216637218474,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2MTE=",
                            "bg_id": "RmlsZToxMzA3MzI=",
                        },
                        {
                            "tag": "Hik TL, N16.5, b0.95, C4, s1",
                            "weight": 0.281154911079988,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2MDU=",
                            "bg_id": "RmlsZToxMzA3MzQ=",
                        },
                        {
                            "tag": "Hik TL, N16.5, b0.95, C4, s1.58",
                            "weight": 0.148371277510384,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2MDM=",
                            "bg_id": "RmlsZToxMzA3MzY=",
                        },
                        {
                            "tag": "Hik TL, N21.5, b1.097, C4, s0.42",
                            "weight": 0.0887399956599006,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1OTk=",
                            "bg_id": "RmlsZToxMzA3Mzg=",
                        },
                        {
                            "tag": "Hik TL, N21.5, b1.097, C4, s1",
                            "weight": 0.169475991711261,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2MDg=",
                            "bg_id": "RmlsZToxMzA3NDA=",
                        },
                        {
                            "tag": "Hik TL, N21.5, b1.097, C4, s1.58",
                            "weight": 0.0894359956258606,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2MTM=",
                            "bg_id": "RmlsZToxMzA3NDI=",
                        },
                        {
                            "tag": "Hik TL, N27.9, b1.241, C4, s0.42",
                            "weight": 0.0192986223768806,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1OTg=",
                            "bg_id": "RmlsZToxMzA3NDQ=",
                        },
                        {
                            "tag": "Hik TL, N27.9, b1.241, C4, s1",
                            "weight": 0.0368565846962387,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1OTA=",
                            "bg_id": "RmlsZToxMzA3NDY=",
                        },
                        {
                            "tag": "Hik TL, N27.9, b1.241, C4, s1.58",
                            "weight": 0.019449984121013,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1OTE=",
                            "bg_id": "RmlsZToxMzA3NDg=",
                        },
                    ],
                },
                {
                    "group": "PUY",
                    "nrlz": 12,
                    "members": [
                        {
                            "tag": "Puy 0.7, N4.6, b0.902, C4, s0.28",
                            "weight": 0.21,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2NTc=",
                            "bg_id": "RmlsZToxMzA3NTM=",
                        },
                        {
                            "tag": "Puy 0.7, N4.6, b0.902, C4, s1",
                            "weight": 0.52,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2NjE=",
                            "bg_id": "RmlsZToxMzA3NTQ=",
                        },
                        {
                            "tag": "Puy 0.7, N4.6, b0.902, C4, s1.72",
                            "weight": 0.27,
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
                            "tag": "geodetic, TI, N2.7, b0.823 C4.2 s1.41",
                            "weight": 0.079403524146159,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MDI=",
                            "bg_id": "RmlsZToxMzA3MTM=",
                        },
                        {
                            "tag": "geodetic, TI, N3.4, b0.959 C4.2 s1.41",
                            "weight": 0.133220340010984,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0OTA=",
                            "bg_id": "RmlsZToxMzA3MjI=",
                        },
                        {
                            "tag": "geodetic, TI, N4.6, b1.089 C4.2 s1.41",
                            "weight": 0.0373761358428573,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0OTQ=",
                            "bg_id": "RmlsZToxMzA3MzE=",
                        },
                        {
                            "tag": "geologic, TI, N2.7, b0.823 C4.2 s1.41",
                            "weight": 0.11158497578786,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0Njg=",
                            "bg_id": "RmlsZToxMzA3MTM=",
                        },
                        {
                            "tag": "geologic, TI, N3.4, b0.959 C4.2 s1.41",
                            "weight": 0.12791016247479,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0Njc=",
                            "bg_id": "RmlsZToxMzA3MjI=",
                        },
                        {
                            "tag": "geologic, TI, N4.6, b1.089 C4.2 s1.41",
                            "weight": 0.0105048617373508,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0NjM=",
                            "bg_id": "RmlsZToxMzA3MzE=",
                        },
                        {
                            "tag": "geodetic, TD, N2.7, b0.823 C4.2 s1.41",
                            "weight": 0.079403524146159,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1NTM=",
                            "bg_id": "RmlsZToxMzA3MTM=",
                        },
                        {
                            "tag": "geodetic, TD, N3.4, b0.959 C4.2 s1.41",
                            "weight": 0.133220340010984,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1NTE=",
                            "bg_id": "RmlsZToxMzA3MjI=",
                        },
                        {
                            "tag": "geodetic, TD, N4.6, b1.089 C4.2 s1.41",
                            "weight": 0.0373761358428573,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1NjI=",
                            "bg_id": "RmlsZToxMzA3MzE=",
                        },
                        {
                            "tag": "geologic, TD, N2.7, b0.823 C4.2 s1.41",
                            "weight": 0.11158497578786,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MjA=",
                            "bg_id": "RmlsZToxMzA3MTM=",
                        },
                        {
                            "tag": "geologic, TD, N3.4, b0.959 C4.2 s1.41",
                            "weight": 0.12791016247479,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MTU=",
                            "bg_id": "RmlsZToxMzA3MjI=",
                        },
                        {
                            "tag": "geologic, TD, N4.6, b1.089 C4.2 s1.41",
                            "weight": 0.0105048617373508,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MzE=",
                            "bg_id": "RmlsZToxMzA3MzE=",
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
