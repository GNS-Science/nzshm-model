gt_description = "Source Logic Tree v9.0.1 IFM Only"

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
            "tag": "Final SLT for TAG Workshop - Hik fix, Cru fix",
            "weight": 1.0,
            "permute": [
                {
                    "group": "Hik",
                    "nrlz": 12,
                    "members": [
                        {
                            "tag": "Hik TL, N16.5, b0.95, C4, s0.42",
                            "weight": 0.147216637218474,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMDg=",
                            "bg_id": "",
                        },
                        {
                            "tag": "Hik TL, N16.5, b0.95, C4, s1",
                            "weight": 0.281154911079988,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMjA=",
                            "bg_id": "",
                        },
                        {
                            "tag": "Hik TL, N16.5, b0.95, C4, s1.58",
                            "weight": 0.148371277510384,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMDc=",
                            "bg_id": "",
                        },
                        {
                            "tag": "Hik TL, N21.5, b1.097, C4, s0.42",
                            "weight": 0.0887399956599006,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMTg=",
                            "bg_id": "",
                        },
                        {
                            "tag": "Hik TL, N21.5, b1.097, C4, s1",
                            "weight": 0.169475991711261,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMTU=",
                            "bg_id": "",
                        },
                        {
                            "tag": "Hik TL, N21.5, b1.097, C4, s1.58",
                            "weight": 0.0894359956258606,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMjE=",
                            "bg_id": "",
                        },
                        {
                            "tag": "Hik TL, N27.9, b1.241, C4, s0.42",
                            "weight": 0.0192986223768806,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMDU=",
                            "bg_id": "",
                        },
                        {
                            "tag": "Hik TL, N27.9, b1.241, C4, s1",
                            "weight": 0.0368565846962387,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMDk=",
                            "bg_id": "",
                        },
                        {
                            "tag": "Hik TL, N27.9, b1.241, C4, s1.58",
                            "weight": 0.019449984121013,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5OTk=",
                            "bg_id": "",
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
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwNzM=",
                            "bg_id": "",
                        },
                        {
                            "tag": "Puy 0.7, N4.6, b0.902, C4, s1",
                            "weight": 0.52,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwNzI=",
                            "bg_id": "",
                        },
                        {
                            "tag": "Puy 0.7, N4.6, b0.902, C4, s1.72",
                            "weight": 0.27,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwNjc=",
                            "bg_id": "",
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
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTQwMjQ=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TI, N2.7, b0.823 C4.2 s1",
                            "weight": 0.0408928149352719,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTM3MDc=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TI, N2.7, b0.823 C4.2 s1.41",
                            "weight": 0.0216771620919014,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTQxMDc=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TI, N3.4, b0.959 C4.2 s0.66",
                            "weight": 0.0282427120823285,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTM4NTQ=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TI, N3.4, b0.959 C4.2 s1",
                            "weight": 0.0686084751056566,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTQxMjg=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TI, N3.4, b0.959 C4.2 s1.41",
                            "weight": 0.0363691528229985,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTQwODA=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TI, N4.6, b1.089 C4.2 s0.66",
                            "weight": 0.00792374079868575,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTM5MTk=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TI, N4.6, b1.089 C4.2 s1",
                            "weight": 0.0192487099590715,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTM1NTA=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TI, N4.6, b1.089 C4.2 s1.41",
                            "weight": 0.0102036850851,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTM4NTA=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TI, N2.7, b0.823 C4.2 s0.66",
                            "weight": 0.0236560148670262,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5MjY=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TI, N2.7, b0.823 C4.2 s1",
                            "weight": 0.0574662625307477,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5MzU=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TI, N2.7, b0.823 C4.2 s1.41",
                            "weight": 0.0304626983900857,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5Mjk=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TI, N3.4, b0.959 C4.2 s0.66",
                            "weight": 0.0271169544446554,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5Mzk=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TI, N3.4, b0.959 C4.2 s1",
                            "weight": 0.0658737336745166,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5NDM=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TI, N3.4, b0.959 C4.2 s1.41",
                            "weight": 0.0349194743556176,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5MTg=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TI, N4.6, b1.089 C4.2 s0.66",
                            "weight": 0.00222703068831837,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5Mjc=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TI, N4.6, b1.089 C4.2 s1",
                            "weight": 0.00541000379473566,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5MzE=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TI, N4.6, b1.089 C4.2 s1.41",
                            "weight": 0.00286782725429677,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5MzM=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TD, N2.7, b0.823 C4.2 s0.66",
                            "weight": 0.0168335471189857,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5NDQ=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TD, N2.7, b0.823 C4.2 s1",
                            "weight": 0.0408928149352719,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5NDk=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TD, N2.7, b0.823 C4.2 s1.41",
                            "weight": 0.0216771620919014,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5NTI=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TD, N3.4, b0.959 C4.2 s0.66",
                            "weight": 0.0282427120823285,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5Njc=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TD, N3.4, b0.959 C4.2 s1",
                            "weight": 0.0686084751056566,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5NjA=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TD, N3.4, b0.959 C4.2 s1.41",
                            "weight": 0.0363691528229985,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5NTQ=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TD, N4.6, b1.089 C4.2 s0.66",
                            "weight": 0.00792374079868575,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5NjM=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TD, N4.6, b1.089 C4.2 s1",
                            "weight": 0.0192487099590715,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5NzA=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geodetic, TD, N4.6, b1.089 C4.2 s1.41",
                            "weight": 0.0102036850851,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5NTk=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TD, N2.7, b0.823 C4.2 s0.66",
                            "weight": 0.0236560148670263,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTU5MzA=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TD, N2.7, b0.823 C4.2 s1",
                            "weight": 0.0574662625307477,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTU5MTc=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TD, N2.7, b0.823 C4.2 s1.41",
                            "weight": 0.0304626983900857,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTY0MTY=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TD, N3.4, b0.959 C4.2 s0.66",
                            "weight": 0.0271169544446554,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTY0NDg=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TD, N3.4, b0.959 C4.2 s1",
                            "weight": 0.0658737336745166,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTY0NDA=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TD, N3.4, b0.959 C4.2 s1.41",
                            "weight": 0.0349194743556176,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTY0NDM=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TD, N4.6, b1.089 C4.2 s0.66",
                            "weight": 0.00222703068831837,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTU5MTA=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TD, N4.6, b1.089 C4.2 s1",
                            "weight": 0.00541000379473566,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTY0Mzg=",
                            "bg_id": "",
                        },
                        {
                            "tag": "geologic, TD, N4.6, b1.089 C4.2 s1.41",
                            "weight": 0.00286782725429677,
                            "inv_id": "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYyOTY0MTM=",
                            "bg_id": "",
                        },
                    ],
                },
            ],
        }
    ]
]
