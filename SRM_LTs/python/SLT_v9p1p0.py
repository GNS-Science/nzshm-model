gt_description = "Source Logic Tree v9.0.1"

src_correlations = {
      "dropped_group": "PUY",
      "correlations":
        [
          [{"group": "Hik", "tag": "Hik TL, N16.5, b0.95, C4, s0.42"}, {"group": "PUY",  "tag": "Puy 0.7, N4.6, b0.902, C4, s0.28" }],
          [{"group": "Hik", "tag": "Hik TL, N16.5, b0.95, C4, s1"}, {"group": "PUY",  "tag": "Puy 0.7, N4.6, b0.902, C4, s1" }],
          [{"group": "Hik", "tag": "Hik TL, N16.5, b0.95, C4, s1.58"}, {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s1.72" }],

          [{"group": "Hik", "tag": "Hik TL, N21.5, b1.097, C4, s0.42"}, {"group": "PUY",  "tag": "Puy 0.7, N4.6, b0.902, C4, s0.28" }],
          [{"group": "Hik", "tag": "Hik TL, N21.5, b1.097, C4, s1"}, {"group": "PUY",  "tag": "Puy 0.7, N4.6, b0.902, C4, s1" }],
          [{"group": "Hik", "tag": "Hik TL, N21.5, b1.097, C4, s1.58"}, {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s1.72" }],

          [{"group": "Hik", "tag": "Hik TL, N27.9, b1.241, C4, s0.42"}, {"group": "PUY",  "tag": "Puy 0.7, N4.6, b0.902, C4, s0.28" }],
          [{"group": "Hik", "tag": "Hik TL, N27.9, b1.241, C4, s1"}, {"group": "PUY",  "tag": "Puy 0.7, N4.6, b0.902, C4, s1" }],
          [{"group": "Hik", "tag": "Hik TL, N27.9, b1.241, C4, s1.58"}, {"group": "PUY", "tag": "Puy 0.7, N4.6, b0.902, C4, s1.72" }]
        ]
    }

logic_tree_permutations = [

    [{
        "tag": "Final SLT for TAG Workshop - Hik fix, Cru fix", "weight": 1.0,
        "permute" : [

            {   "group": "Hik",
                "nrlz": 12,
                "members" : [
                    {"tag": "Hik TL, N16.5, b0.95, C4, s0.42", "weight": 0.147216637218474, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMDg=", "bg_id": "RmlsZToxMzA3MzI="},
                    {"tag": "Hik TL, N16.5, b0.95, C4, s1", "weight": 0.281154911079988, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMjA=", "bg_id": "RmlsZToxMzA3MzQ="},
                    {"tag": "Hik TL, N16.5, b0.95, C4, s1.58", "weight": 0.148371277510384, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMDc=", "bg_id": "RmlsZToxMzA3MzY="},
                    {"tag": "Hik TL, N21.5, b1.097, C4, s0.42", "weight": 0.0887399956599006, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMTg=", "bg_id": "RmlsZToxMzA3Mzg="},
                    {"tag": "Hik TL, N21.5, b1.097, C4, s1", "weight": 0.169475991711261, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMTU=", "bg_id": "RmlsZToxMzA3NDA="},
                    {"tag": "Hik TL, N21.5, b1.097, C4, s1.58", "weight": 0.0894359956258606, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMjE=", "bg_id": "RmlsZToxMzA3NDI="},
                    {"tag": "Hik TL, N27.9, b1.241, C4, s0.42", "weight": 0.0192986223768806, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMDU=", "bg_id": "RmlsZToxMzA3NDQ="},
                    {"tag": "Hik TL, N27.9, b1.241, C4, s1", "weight": 0.0368565846962387, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwMDk=", "bg_id": "RmlsZToxMzA3NDY="},
                    {"tag": "Hik TL, N27.9, b1.241, C4, s1.58", "weight": 0.019449984121013, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjM5OTk=", "bg_id": "RmlsZToxMzA3NDg="},
                ]
            },

            {   "group": "PUY",
                "nrlz": 12,
                "members" : [
                    {"tag": "Puy 0.7, N4.6, b0.902, C4, s0.28", "weight": 0.21, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwNzM=", "bg_id": "RmlsZToxMzA3NTM="},
                    {"tag": "Puy 0.7, N4.6, b0.902, C4, s1", "weight": 0.52, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwNzI=", "bg_id": "RmlsZToxMzA3NTQ="},
                    {"tag": "Puy 0.7, N4.6, b0.902, C4, s1.72", "weight": 0.27, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMjQwNjc=", "bg_id": "RmlsZToxMzA3NTU="},
                ]
            },

             {  "group": "CRU",
                "nrlz": 21,
                "members" : [
                    {"tag": "geodetic, TI, N2.7, b0.823 C4.2 s0.66", "weight": 0.0168335471189857, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwMTA=", "bg_id": "RmlsZToxMzA3MDc="},
                    {"tag": "geodetic, TI, N2.7, b0.823 C4.2 s1", "weight": 0.0408928149352719, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwMjE=", "bg_id": "RmlsZToxMzA3MTA="},
                    {"tag": "geodetic, TI, N2.7, b0.823 C4.2 s1.41", "weight": 0.0216771620919014, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwMjA=", "bg_id": "RmlsZToxMzA3MTM="},
                    {"tag": "geodetic, TI, N3.4, b0.959 C4.2 s0.66", "weight": 0.0282427120823285, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwMDY=", "bg_id": "RmlsZToxMzA3MTY="},
                    {"tag": "geodetic, TI, N3.4, b0.959 C4.2 s1", "weight": 0.0686084751056566, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwMTI=", "bg_id": "RmlsZToxMzA3MTk="},
                    {"tag": "geodetic, TI, N3.4, b0.959 C4.2 s1.41", "weight": 0.0363691528229985, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwMDM=", "bg_id": "RmlsZToxMzA3MjI="},
                    {"tag": "geodetic, TI, N4.6, b1.089 C4.2 s0.66", "weight": 0.00792374079868575, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwMDc=", "bg_id": "RmlsZToxMzA3MjU="},
                    {"tag": "geodetic, TI, N4.6, b1.089 C4.2 s1", "weight": 0.0192487099590715, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzM5OTg=", "bg_id": "RmlsZToxMzA3Mjg="},
                    {"tag": "geodetic, TI, N4.6, b1.089 C4.2 s1.41", "weight": 0.0102036850851, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwMDI=", "bg_id": "RmlsZToxMzA3MzE="},

                    {"tag": "geologic, TI, N2.7, b0.823 C4.2 s0.66", "weight": 0.0236560148670262, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzM5NzI=", "bg_id": "RmlsZToxMzA3MDc="},
                    {"tag": "geologic, TI, N2.7, b0.823 C4.2 s1", "weight": 0.0574662625307477, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzM5NzM=", "bg_id": "RmlsZToxMzA3MTA="},
                    {"tag": "geologic, TI, N2.7, b0.823 C4.2 s1.41", "weight": 0.0304626983900857, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzM5ODI=", "bg_id": "RmlsZToxMzA3MTM="},
                    {"tag": "geologic, TI, N3.4, b0.959 C4.2 s0.66", "weight": 0.0271169544446554, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzM5Nzk=", "bg_id": "RmlsZToxMzA3MTY="},
                    {"tag": "geologic, TI, N3.4, b0.959 C4.2 s1", "weight": 0.0658737336745166, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzM5ODA=", "bg_id": "RmlsZToxMzA3MTk="},
                    {"tag": "geologic, TI, N3.4, b0.959 C4.2 s1.41", "weight": 0.0349194743556176, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzM5Njg=", "bg_id": "RmlsZToxMzA3MjI="},
                    {"tag": "geologic, TI, N4.6, b1.089 C4.2 s0.66", "weight": 0.00222703068831837, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzM5NzA=", "bg_id": "RmlsZToxMzA3MjU="},
                    {"tag": "geologic, TI, N4.6, b1.089 C4.2 s1", "weight": 0.00541000379473566, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzM5OTI=", "bg_id": "RmlsZToxMzA3Mjg="},
                    {"tag": "geologic, TI, N4.6, b1.089 C4.2 s1.41", "weight": 0.00286782725429677, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzM5ODg=", "bg_id": "RmlsZToxMzA3MzE="},

                    {"tag": "geodetic, TD, N2.7, b0.823 C4.2 s0.66", "weight": 0.0168335471189857, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwNTY=", "bg_id": "RmlsZToxMzA3MDc="},
                    {"tag": "geodetic, TD, N2.7, b0.823 C4.2 s1", "weight": 0.0408928149352719, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwNTQ=", "bg_id": "RmlsZToxMzA3MTA="},
                    {"tag": "geodetic, TD, N2.7, b0.823 C4.2 s1.41", "weight": 0.0216771620919014, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwNjU=", "bg_id": "RmlsZToxMzA3MTM="},
                    {"tag": "geodetic, TD, N3.4, b0.959 C4.2 s0.66", "weight": 0.0282427120823285, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwNTI=", "bg_id": "RmlsZToxMzA3MTY="},
                    {"tag": "geodetic, TD, N3.4, b0.959 C4.2 s1", "weight": 0.0686084751056566, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwNTc=", "bg_id": "RmlsZToxMzA3MTk="},
                    {"tag": "geodetic, TD, N3.4, b0.959 C4.2 s1.41", "weight": 0.0363691528229985, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwNzM=", "bg_id": "RmlsZToxMzA3MjI="},
                    {"tag": "geodetic, TD, N4.6, b1.089 C4.2 s0.66", "weight": 0.00792374079868575, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwNjM=", "bg_id": "RmlsZToxMzA3MjU="},
                    {"tag": "geodetic, TD, N4.6, b1.089 C4.2 s1", "weight": 0.0192487099590715, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwNzU=", "bg_id": "RmlsZToxMzA3Mjg="},
                    {"tag": "geodetic, TD, N4.6, b1.089 C4.2 s1.41", "weight": 0.0102036850851, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwNjE=", "bg_id": "RmlsZToxMzA3MzE="},

                    {"tag": "geologic, TD, N2.7, b0.823 C4.2 s0.66", "weight": 0.0236560148670263, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwNDM=", "bg_id": "RmlsZToxMzA3MDc="},
                    {"tag": "geologic, TD, N2.7, b0.823 C4.2 s1", "weight": 0.0574662625307477, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwNDE=", "bg_id": "RmlsZToxMzA3MTA="},
                    {"tag": "geologic, TD, N2.7, b0.823 C4.2 s1.41", "weight": 0.0304626983900857, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwMjY=", "bg_id": "RmlsZToxMzA3MTM="},
                    {"tag": "geologic, TD, N3.4, b0.959 C4.2 s0.66", "weight": 0.0271169544446554, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwMzY=", "bg_id": "RmlsZToxMzA3MTY="},
                    {"tag": "geologic, TD, N3.4, b0.959 C4.2 s1", "weight": 0.0658737336745166, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwMzI=", "bg_id": "RmlsZToxMzA3MTk="},
                    {"tag": "geologic, TD, N3.4, b0.959 C4.2 s1.41", "weight": 0.0349194743556176, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwMjg=", "bg_id": "RmlsZToxMzA3MjI="},
                    {"tag": "geologic, TD, N4.6, b1.089 C4.2 s0.66", "weight": 0.00222703068831837, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwNDQ=", "bg_id": "RmlsZToxMzA3MjU="},
                    {"tag": "geologic, TD, N4.6, b1.089 C4.2 s1", "weight": 0.00541000379473566, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwNDI=", "bg_id": "RmlsZToxMzA3Mjg="},
                    {"tag": "geologic, TD, N4.6, b1.089 C4.2 s1.41", "weight": 0.00286782725429677, "inv_id":"SW52ZXJzaW9uU29sdXRpb25Ocm1sOjYzMzQwMzU=", "bg_id": "RmlsZToxMzA3MzE="},
                ]
             },



            {   "group": "SLAB",
                "nrlz": 12,
                "members" : [
                    {"tag": "slab-uniform-1depth-rates", "weight":1.0,"inv_id":"", "bg_id":"RmlsZToxMjEwMzM="}
                ]
            }

        ]
    }]

]
