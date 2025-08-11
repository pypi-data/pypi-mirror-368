
def NBI_42a(key):
    # https://www.fhwa.dot.gov/bridge/mtguide.pdf
    table = {
        "Building or plaza":          "0",

        "Other":                      "0",
        "Highway":                    "1",
        "Railroad":                   "2",
        "Highway-railroad":           "4",
        "Highway-pedestrian":         "5",
        "Overpass structure at an interchange or second level of a multilevel interchange": "6",
        "Fourth level (Interchange)": "8",
        "Third level (Interchange)":  "7",
    }
    return f"{table[key]} - {key}"

def NBI_42b(string):
    """
    "Highway, with or without pedestrian"
    Highway-railroad
    Highway-waterway
    Highway-waterway-railroad
    Other
    Railroad
    Railroad-waterway
    Relief for waterway
    Waterway
"""

def NBI_43b(string):
    pass
