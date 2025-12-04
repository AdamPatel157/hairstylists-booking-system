def user_friendly_service_names(serviceName):
    mapping = {
        "MachineOnly": "Machine Only",
        "MachineAndScissor": "Machine and Scissors",
        "SkinFade": "Skin Fade",
        "WaterOnlyRinse": "Water-Only Rinse",
        "ShampooWash": "Shampoo Wash",
        "ShampooAndConditionerWash": "Shampoo and Conditioner Wash",
        "BlackDye": "Black",
        "DarkBrownDye": "Dark Brown",
        "MediumBrownDye": "Medium Brown",
        "LightBrownDye": "Light Brown",
        "BlondeDye": "Blonde",
        "Bleach": "Bleach",
        "BeardTrim": "Trim Only",
        "BeardLineup": "Lineup Only",
        "BeardTrimAndLineup": "Trim and Lineup",
        "BeardCleanShave": "Clean Shave",
        "BeardOil": "Beard Oil",
        "BeardFragrance": "Beard Fragrance",
        "HotTowel": "Hot Towel"
    }
    return mapping.get(serviceName, serviceName)

def user_friendly_category_names(categoryName):
    mapping = {
        "Haircuts": "Haircuts",
        "HairWashAndDry": "Hair Wash and Dry",
        "HairColour": "Hair Colour",
        "BeardStyling": "Beard Styling",
        "BeardWashAndDry": "Beard Wash and Dry",
        "BeardMiscellaneous": "Beard Miscellaneous"
    }
    return mapping.get(categoryName, categoryName)