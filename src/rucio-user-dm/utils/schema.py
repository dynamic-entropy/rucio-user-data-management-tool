from strictyaml import Map, Str, Int, Seq, Optional


datasetSchema = Map(
    {
        "kind": Str(),
        Optional("metadata"): Map({
            "name": Str()
        }),
        "specs": Map({
            "datasetPath": Str(),
            "datasetName": Str(),
            "options": Map({
                "upload": Map({
                    "tempRSE": Str()
                }),
                "rule": Map({
                    "rse": Str(),
                    "copies": Int(),
                    "lifetime": Int()
                })
            }),
            Optional("lfnMap"): Seq(Map({"name": Str(), "lfn":Str() }))
        })
    }
)


fileSchema = Map(
    {
        "kind": Str(),
        Optional("metadata"): Map({
            "name": Str()
        }),
        "specs": Map({
            "filePath": Str(),
            "lfn": Str(),
            "options": Map({
                "upload": Map({
                    "tempRSE": Str()
                }),
                "rule": Map({
                    "rse": Str(),
                    "copies": Int(),
                    "lifetime": Int(),
                })
            }),

        })
    }
)