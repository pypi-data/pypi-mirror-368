DEFAULT_TEMPLATE = {
    "version": "0.0.5",
    "naming_convention": {
        "sep": "_",
        "structure": [
            "year",
            "summary",
            "internal",
            "researcherName",
            "organisationName",
        ],
    },
    "layout": {
        "structure": ["site", "sensor", "date", "trial", "procLevel"],
        "mapping": {"procLevel": {"raw": "T0-raw", "proc": "T1-proc", "trait": "T2-trait"}},
    },
    "file": {
        "*": {
            "sep": "_",
            "default": {"procLevel": "raw"},
            "components": [
                {"sep": "-", "components": [["date", r"\d{8}"], ["time", r"\d{6}"]]},
                ["site", "[^_.]+"],
                ["sensor", "[^_.]+"],
                ["trial", "[^_.]+"],
                {
                    "name": "procLevel",
                    "pattern": "T0-raw|T1-proc|T2-trait|raw|proc|trait",
                    "required": False,
                },
            ],
        }
    },
}
