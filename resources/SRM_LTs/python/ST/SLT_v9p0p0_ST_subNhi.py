gt_description = "Source Logic Tree v9.0.0"

src_correlations = {
    "dropped_group": "PUY",
    "correlations": [
        [
            {"group": "Hik", "tag": "Hik TL, N16.5, b0.95, C4, s1.58"},
            {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s1.72"},
        ],
        [
            {"group": "Hik", "tag": "Hik TL, N21.5, b1.097, C4, s1.58"},
            {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s1.72"},
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
                            "tag": "Hik TL, N16.5, b0.95, C4, s1.58",
                            "weight": 0.576742825808845,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2MDM=",
                            "bg_id": "RmlsZToxMzA3MzY=",
                        },
                        {
                            "tag": "Hik TL, N21.5, b1.097, C4, s1.58",
                            "weight": 0.347651982997022,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2MTM=",
                            "bg_id": "RmlsZToxMzA3NDI=",
                        },
                        {
                            "tag": "Hik TL, N27.9, b1.241, C4, s1.58",
                            "weight": 0.0756051911941323,
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
                            "tag": "geodetic, TI, N2.7, b0.823 C4.2 s0.66",
                            "weight": 0.0168335471189857,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MDE=",
                            "bg_id": "RmlsZToxMzA3MDc=",
                        },
                        {
                            "tag": "geodetic, TI, N2.7, b0.823 C4.2 s1",
                            "weight": 0.0408928149352719,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0ODY=",
                            "bg_id": "RmlsZToxMzA3MTA=",
                        },
                        {
                            "tag": "geodetic, TI, N2.7, b0.823 C4.2 s1.41",
                            "weight": 0.0216771620919014,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MDI=",
                            "bg_id": "RmlsZToxMzA3MTM=",
                        },
                        {
                            "tag": "geodetic, TI, N3.4, b0.959 C4.2 s0.66",
                            "weight": 0.0282427120823285,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0ODI=",
                            "bg_id": "RmlsZToxMzA3MTY=",
                        },
                        {
                            "tag": "geodetic, TI, N3.4, b0.959 C4.2 s1",
                            "weight": 0.0686084751056566,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0ODM=",
                            "bg_id": "RmlsZToxMzA3MTk=",
                        },
                        {
                            "tag": "geodetic, TI, N3.4, b0.959 C4.2 s1.41",
                            "weight": 0.0363691528229985,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0OTA=",
                            "bg_id": "RmlsZToxMzA3MjI=",
                        },
                        {
                            "tag": "geodetic, TI, N4.6, b1.089 C4.2 s0.66",
                            "weight": 0.00792374079868575,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0OTE=",
                            "bg_id": "RmlsZToxMzA3MjU=",
                        },
                        {
                            "tag": "geodetic, TI, N4.6, b1.089 C4.2 s1",
                            "weight": 0.0192487099590715,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0OTY=",
                            "bg_id": "RmlsZToxMzA3Mjg=",
                        },
                        {
                            "tag": "geodetic, TI, N4.6, b1.089 C4.2 s1.41",
                            "weight": 0.0102036850851,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0OTQ=",
                            "bg_id": "RmlsZToxMzA3MzE=",
                        },
                        {
                            "tag": "geologic, TI, N2.7, b0.823 C4.2 s0.66",
                            "weight": 0.0236560148670262,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0NzM=",
                            "bg_id": "RmlsZToxMzA3MDc=",
                        },
                        {
                            "tag": "geologic, TI, N2.7, b0.823 C4.2 s1",
                            "weight": 0.0574662625307477,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0ODE=",
                            "bg_id": "RmlsZToxMzA3MTA=",
                        },
                        {
                            "tag": "geologic, TI, N2.7, b0.823 C4.2 s1.41",
                            "weight": 0.0304626983900857,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0Njg=",
                            "bg_id": "RmlsZToxMzA3MTM=",
                        },
                        {
                            "tag": "geologic, TI, N3.4, b0.959 C4.2 s0.66",
                            "weight": 0.0271169544446554,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0NjQ=",
                            "bg_id": "RmlsZToxMzA3MTY=",
                        },
                        {
                            "tag": "geologic, TI, N3.4, b0.959 C4.2 s1",
                            "weight": 0.0658737336745166,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0NzY=",
                            "bg_id": "RmlsZToxMzA3MTk=",
                        },
                        {
                            "tag": "geologic, TI, N3.4, b0.959 C4.2 s1.41",
                            "weight": 0.0349194743556176,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0Njc=",
                            "bg_id": "RmlsZToxMzA3MjI=",
                        },
                        {
                            "tag": "geologic, TI, N4.6, b1.089 C4.2 s0.66",
                            "weight": 0.00222703068831837,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0NjA=",
                            "bg_id": "RmlsZToxMzA3MjU=",
                        },
                        {
                            "tag": "geologic, TI, N4.6, b1.089 C4.2 s1",
                            "weight": 0.00541000379473566,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0NzU=",
                            "bg_id": "RmlsZToxMzA3Mjg=",
                        },
                        {
                            "tag": "geologic, TI, N4.6, b1.089 C4.2 s1.41",
                            "weight": 0.00286782725429677,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE0NjM=",
                            "bg_id": "RmlsZToxMzA3MzE=",
                        },
                        {
                            "tag": "geodetic, TD, N2.7, b0.823 C4.2 s0.66",
                            "weight": 0.0168335471189857,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1Mzk=",
                            "bg_id": "RmlsZToxMzA3MDc=",
                        },
                        {
                            "tag": "geodetic, TD, N2.7, b0.823 C4.2 s1",
                            "weight": 0.0408928149352719,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1Mzc=",
                            "bg_id": "RmlsZToxMzA3MTA=",
                        },
                        {
                            "tag": "geodetic, TD, N2.7, b0.823 C4.2 s1.41",
                            "weight": 0.0216771620919014,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1NTM=",
                            "bg_id": "RmlsZToxMzA3MTM=",
                        },
                        {
                            "tag": "geodetic, TD, N3.4, b0.959 C4.2 s0.66",
                            "weight": 0.0282427120823285,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1NDQ=",
                            "bg_id": "RmlsZToxMzA3MTY=",
                        },
                        {
                            "tag": "geodetic, TD, N3.4, b0.959 C4.2 s1",
                            "weight": 0.0686084751056566,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1NTk=",
                            "bg_id": "RmlsZToxMzA3MTk=",
                        },
                        {
                            "tag": "geodetic, TD, N3.4, b0.959 C4.2 s1.41",
                            "weight": 0.0363691528229985,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1NTE=",
                            "bg_id": "RmlsZToxMzA3MjI=",
                        },
                        {
                            "tag": "geodetic, TD, N4.6, b1.089 C4.2 s0.66",
                            "weight": 0.00792374079868575,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1NTg=",
                            "bg_id": "RmlsZToxMzA3MjU=",
                        },
                        {
                            "tag": "geodetic, TD, N4.6, b1.089 C4.2 s1",
                            "weight": 0.0192487099590715,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1NDE=",
                            "bg_id": "RmlsZToxMzA3Mjg=",
                        },
                        {
                            "tag": "geodetic, TD, N4.6, b1.089 C4.2 s1.41",
                            "weight": 0.0102036850851,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1NjI=",
                            "bg_id": "RmlsZToxMzA3MzE=",
                        },
                        {
                            "tag": "geologic, TD, N2.7, b0.823 C4.2 s0.66",
                            "weight": 0.0236560148670263,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MjI=",
                            "bg_id": "RmlsZToxMzA3MDc=",
                        },
                        {
                            "tag": "geologic, TD, N2.7, b0.823 C4.2 s1",
                            "weight": 0.0574662625307477,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MjM=",
                            "bg_id": "RmlsZToxMzA3MTA=",
                        },
                        {
                            "tag": "geologic, TD, N2.7, b0.823 C4.2 s1.41",
                            "weight": 0.0304626983900857,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MjA=",
                            "bg_id": "RmlsZToxMzA3MTM=",
                        },
                        {
                            "tag": "geologic, TD, N3.4, b0.959 C4.2 s0.66",
                            "weight": 0.0271169544446554,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MTY=",
                            "bg_id": "RmlsZToxMzA3MTY=",
                        },
                        {
                            "tag": "geologic, TD, N3.4, b0.959 C4.2 s1",
                            "weight": 0.0658737336745166,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1Mjk=",
                            "bg_id": "RmlsZToxMzA3MTk=",
                        },
                        {
                            "tag": "geologic, TD, N3.4, b0.959 C4.2 s1.41",
                            "weight": 0.0349194743556176,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MTU=",
                            "bg_id": "RmlsZToxMzA3MjI=",
                        },
                        {
                            "tag": "geologic, TD, N4.6, b1.089 C4.2 s0.66",
                            "weight": 0.00222703068831837,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MzM=",
                            "bg_id": "RmlsZToxMzA3MjU=",
                        },
                        {
                            "tag": "geologic, TD, N4.6, b1.089 C4.2 s1",
                            "weight": 0.00541000379473566,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MjY=",
                            "bg_id": "RmlsZToxMzA3Mjg=",
                        },
                        {
                            "tag": "geologic, TD, N4.6, b1.089 C4.2 s1.41",
                            "weight": 0.00286782725429677,
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
