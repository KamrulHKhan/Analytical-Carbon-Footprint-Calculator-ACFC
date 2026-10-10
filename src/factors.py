"""Selectable items displayed in the ACFC user interface."""

import pandas as pd

GRID_DEFAULT = 0.3288  # kg CO2e/kWh

MOBILE_PHASES = {
    "HPLC": [
        {"name": "Acetonitrile"},
        {"name": "Water"},
        {"name": "Ethanol"},
        {"name": "Isopropyl Alcohol"},
        {"name": "Methanol"}
    ],

    "UHPLC": [
        {"name": "Acetonitrile"},
        {"name": "Water"},
        {"name": "Ethanol"},
        {"name": "Isopropyl Alcohol"},
        {"name": "Methanol"}
    ],

    "GC": [
        {"name": "Helium"},
        {"name": "Hydrogen"},
        {"name": "Nitrogen"}
    ],

    "SFC": [
        {"name": "Carbon Dioxide"},
        {"name": "Methanol"}
    ]
}

OTHER_CHEMICALS = [
    {"name": "Acetic Acid"},
    {"name": "Acetone"},
    {"name": "Ammonium Acetate"},
    {"name": "Ammonium Chloride"},
    {"name": "Ammonium Dihydrogen Phosphate"},
    {"name": "Ammonium Formate"},
    {"name": "Ammonium Hydroxide"},
    {"name": "Anisole"},
    {"name": "Cyclohexane"},
    {"name": "Dichloromethane"},
    {"name": "Di-Isopropyl Ether"},
    {"name": "Dimethyl Sulfoxide"},
    {"name": "Dimethylformamide"},
    {"name": "EDTA"},
    {"name": "Ethanol"},
    {"name": "Ethyl Acetate"},
    {"name": "Formic Acid"},
    {"name": "Heptane"},
    {"name": "Hydrochloric Acid"},
    {"name": "Isopropylamine"},
    {"name": "MSA"},
    {"name": "Methyl Pyrrolidone"},
    {"name": "MTBE"},
    {"name": "Monobasic Potassium Phosphate"},
    {"name": "Hexane"},
    {"name": "DMAC"},
    {"name": "Orthophosphoric Acid"},
    {"name": "Phosphoric Acid"},
    {"name": "Potassium Dihydrogen Phosphate"},
    {"name": "Potassium Phosphate Monobasic"},
    {"name": "Sodium Benzoate"},
    {"name": "NaCl"},
    {"name": "SDS"},
    {"name": "THF"},
    {"name": "Toluene"},
    {"name": "TEA"},
    {"name": "TFA"},
    {"name": "Trifluorotoluene"},
    {"name": "K3PO4"},
    {"name": "TRIS"},
    {"name": "DMI"}
]

CONSUMABLES = {
    "General": [
        {"name": "Gloves"},
        {"name": "Syringe"},
        {"name": "Paper Towel"},
        {"name": "Plastic Bulb Pipette"},
        {"name": "LC Vial"},
        {"name": "Weigh Funnel and Spatula"}
    ],

    "HPLC": [],

    "UHPLC": [],

    "GC": [
        {"name": "Headspace Vial"},
        {"name": "Septum"}
    ],

    "SFC": []
}

ANALYTICAL_INSTRUMENTS = {
    "HPLC": [
        {"name": "Agilent 1260"}
    ],

    "UHPLC": [
        {"name": "Waters UPLC"},
        {"name": "Agilent 1290"}
    ],

    "GC": [
        {"name": "Agilent 7890 GC"}
    ],

    "SFC": [
        {"name": "Waters UPC2"}
    ]
}

GAS_GENERATORS = {
    "HPLC": [],

    "UHPLC": [],

    "GC": [
        {"name": "Zero Air Generator"},
        {"name": "Nitrogen Generator"},
        {"name": "Hydrogen Generator"}
    ],

    "SFC": []
}

GENERAL_LAB_EQUIPMENT = {
    "General": [
        {"name": "Ultra Sonic Bath"},
        {"name": "Stirrer Plate"},
        {"name": "Vortexer"},
        {"name": "Drying Oven"},
    ],

    "GC": [
        {"name": "Crimper"}
    ]
}


SOLVENT_PACKAGING_ITEM_NAMES_EXCLUDED = [
    "Carbon Dioxide", 
    "Water",
    "Nitrogen",
    "Helium",
    "Hydrogen"
    ]

SOLVENT_WASTE_ITEM_NAMES_EXCLUDED = [
    "Carbon Dioxide", 
    "Nitrogen",
    "Helium",
    "Hydrogen"
    ]

GAS_TRANSPORTATION_ITEM_NAMES = [
    "Carbon Dioxide", 
    "Nitrogen",
    "Helium"
]

INSTRUMENT_POWER = pd.DataFrame(
    {
        "Name": ["Waters UPLC", "Agilent 1290", "Agilent 1260", "Waters UPC2", "Agilent 7890 GC"],
        "idle": [182.00, 107.00, 115.00, 287.00, 195.52],
        "run":  [319.00, 171.00, 141.00, 432.00, 756.77]
    },
)

