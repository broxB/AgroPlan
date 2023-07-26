import enum

__all__ = [
    "FieldType",
    "FieldTypeForCrops",
    "SoilType",
    "HumusType",
    "CropType",
    "CropClass",
    "CultivationType",
    "CultivationType",
    "MainCultivationType",
    "CutTiming",
    "ResidueType",
    "MainCropResidueType",
    "CatchCropResidueType",
    "LegumeType",
    "GrasslandLegumeType",
    "MainCropLegumeType",
    "CatchCropLegumeType",
    "FertClass",
    "FertType",
    "OrganicFertType",
    "MineralFertType",
    "NFertType",
    "BasicFertType",
    "MiscFertType",
    "LimeFertType",
    "MeasureType",
    "OrganicMeasureType",
    "MineralMeasureType",
    "NMeasureType",
    "BasicMeasureType",
    "MiscMeasureType",
    "LimeMeasureType",
    "NminType",
    "UnitType",
    "DemandType",
    "NutrientType",
]


class FieldType(enum.Enum):
    """Field types: `cropland`, `fallow_grassland`, `exchanged_land` etc."""

    grassland = "Grünland"
    cropland = "Ackerland"
    exchanged_land = "Tauschfläche"
    fallow_grassland = "Grünland-Brache"
    fallow_cropland = "Ackerland-Brache"


FieldTypeForCrops: enum.Enum = enum.Enum(
    "FieldTypeForCrops", [(e.name, e.value) for e in FieldType if e.name != "exchanged_land"]
)


class SoilType(enum.Enum):
    """Soil compositions: `sand`, `strong_loamy_sand` etc."""

    sand = "Sand"
    light_loamy_sand = "schwach lehmiger Sand"
    strong_loamy_sand = "stark lehmiger Sand"
    sandy_to_silty_loam = "sand. bis schluff. Lehm"
    clayey_loam_to_clay = "toniger Lehm bis Ton"
    moor = "Niedermoor"


class HumusType(enum.Enum):
    """Humus content ratios for soil samples: `less_4`, `less_15` etc."""

    less_4 = r"< 4%"
    less_8 = r"4% bis < 8%"
    less_15 = r"8% bis < 15%"
    less_30 = r"15% bis < 30%"
    more_30 = r">= 30%"


class CropType(enum.Enum):
    """Fruit groups for preceding crop effect: `canola`, `grain` and `permanent_grassland` etc."""

    # Hauptfrüchte
    rotating_fallow_with_legume = "Rotationsbrache mit Leguminosen"
    rotating_fallow = "Rotationsbrache ohne Leguminosen"
    permanent_fallow = "Dauerbrache"
    permanent_grassland = "Dauergrünland"
    alfalfa = "Luzerne"
    alfalfa_grass = "Luzernegras"
    clover = "Klee"
    clover_grass = "Kleegras"
    sugar_beets = "Zuckerrüben"
    canola = "Raps"
    legume_grain = "Körnerleguminosen"
    cabbage = "Kohlgemüse"
    field_grass = "Acker-/Saatgras"
    grain = "Getreide"
    corn = "Mais"
    potato = "Kartoffel"
    vegetable = "Gemüse ohne Kohlarten"
    # Zwischenfrüchte
    catch_non_legume = "Nichtleguminosen"
    catch_legume = "Leguminosen"
    catch_other = "andere Zwischenfrüchte"


class CultivationType(enum.Enum):
    """Cultivation classes for crop rotation: `main_crop` etc."""

    catch_crop = "Zwischenfrucht"
    main_crop = "Hauptfrucht"
    second_main_crop = "Zweite Hauptfrucht"
    second_crop = "Zweitfrucht"


# no second crop implemented yet. no database data support.
UsedCultivationType: enum.Enum = enum.Enum(
    "UsedCultivationType",
    [(e.name, e.value) for e in CultivationType if e is not CultivationType.second_crop],
)


MainCultivationType: enum.Enum = enum.Enum(
    "MainCultivationType", [(e.name, e.value) for e in CultivationType if "main" in e.name]
)


class CutTiming(enum.Enum):
    """Different cut timings for mowable crops: `first_cut`, `second_cut` etc."""

    first_cut = "1. Schnitt"
    second_cut = "2. Schnitt"
    third_cut = "3. Schnitt"
    fourth_cut = "4. Schnitt"
    non_mowable = "nicht mähbar"


class CropClass(enum.Enum):
    """Crop classes for classification: `catch_crop` and `main_crop`"""

    catch_crop = "Zwischenfrucht"
    main_crop = "Hauptfrucht"
    second_crop = "Zweitfrucht"


class ResidueType(enum.Enum):
    """Crop residues for preceding crop effect: `stayed`, `removed` or `frozen`, `catch_crop_used` etc."""

    # Hauptfrüchte
    main_stayed = "verbleibt"
    main_removed = "abgefahren"
    main_no_residues = "keine"
    # Zwischenfrüchte
    catch_frozen = "abgefroren"
    catch_not_frozen_fall = "nicht abgefroren, eingearbeitet Herbst"
    catch_not_frozen_spring = "nicht abgefroren, eingearbeitet Frühjahr"
    catch_used = "mit Nutzung"


MainCropResidueType: enum.Enum = enum.Enum(
    "MainCropResidueType", [(e.name, e.value) for e in ResidueType if "main_" in e.name]
)
CatchCropResidueType: enum.Enum = enum.Enum(
    "CatchCropResidueType", [(e.name, e.value) for e in ResidueType if "catch_" in e.name]
)


class LegumeType(enum.Enum):
    """Ratio of legumes in fruits: `grass_less_10`, `crop_10`, `catch_25` etc."""

    # Grünland
    grass_less_5 = r"< 5%"
    grass_less_10 = r"5% bis 10%"
    grass_less_20 = r"> 10% bis 20%"
    grass_greater_20 = r"> 20%"
    # Ackerland
    main_crop_0 = r"< 10%"
    main_crop_10 = r"10% - 19%"
    main_crop_20 = r"20% - 29%"
    main_crop_30 = r"30% - 39%"
    main_crop_40 = r"40% - 49%"
    main_crop_50 = r"50% - 59%"
    main_crop_60 = r"60% - 69%"
    main_crop_70 = r"70% - 79%"
    main_crop_80 = r"80% - 89%"
    main_crop_90 = r"90% - 99%"
    main_crop_100 = r"100%"
    # Zwischenfrucht
    catch_25 = r"< 25%"
    catch_50 = r"25% bis 75%"
    catch_75 = r"> 75%"
    none = r"0%"


GrasslandLegumeType: enum.Enum = enum.Enum(
    "GrasslandLegumeType", [(e.name, e.value) for e in LegumeType if "grass_" in e.name]
)
MainCropLegumeType: enum.Enum = enum.Enum(
    "MainCropLegumeType", [(e.name, e.value) for e in LegumeType if "main_" in e.name]
)
CatchCropLegumeType: enum.Enum = enum.Enum(
    "CatchCropLegumeType", [(e.name, e.value) for e in LegumeType if "catch_" in e.name]
)


class FertClass(enum.Enum):
    """Fertilizer basic classifications: `organic` or `mineral`"""

    organic = "Wirtschaftsdünger"
    mineral = "Mineraldünger"


class FertType(enum.Enum):
    """Fertilizer subtype classifications: `slurry`, `digestate` or `n_p_k`, `lime` etc."""

    # organic
    org_digestate = "Gärrest"
    org_slurry = "Gülle"
    org_manure = "Festmist"
    org_dry_manure = "Trockenkot"
    org_compost = "Kompost"
    # mineral
    k = "K"
    n = "N"
    n_k = "N/K"
    n_p = "N/P"
    n_s = "N+S"
    n_p_k = "NPK"
    n_p_k_s = "NPKS"
    p = "P"
    p_k = "P/K"
    lime = "Kalk"
    misc = "Sonstige"
    auxiliary = "Hilfsstoffe"


OrganicFertType: enum.Enum = enum.Enum(
    "OrganicFertType", [(e.name, e.value) for e in FertType if "org_" in e.name]
)
MineralFertType: enum.Enum = enum.Enum(
    "MineralFertType", [(e.name, e.value) for e in FertType if "org_" not in e.name]
)

NFertType: enum.Enum = enum.Enum(
    "NFertType",
    [(e.name, e.value) for e in FertType if e.name.startswith("n") or e.name == "n"],
)
BasicFertType: enum.Enum = enum.Enum(
    "BasicFertType",
    [(e.name, e.value) for e in FertType if e.name.startswith("p") or e.name.startswith("k")],
)
MiscFertType: enum.Enum = enum.Enum(
    "MiscFertType", [(e.name, e.value) for e in (FertType.misc, FertType.auxiliary)]
)
LimeFertType: enum.Enum = enum.Enum("LimeFertType", [FertType.lime.name, FertType.lime.value])


class MeasureType(enum.Enum):
    """Measures for fertilization: `fall`, `first_n_fert`, `lime_fert` etc."""

    org_fall = "Herbst"
    org_spring = "Frühjahr"
    first_first_n_fert = "1.1 N-Gabe"
    first_second_n_fert = "1.2 N-Gabe"
    first_n_fert = "1. N-Gabe"
    second_n_fert = "2. N-Gabe"
    third_n_fert = "3. N-Gabe"
    fourth_n_fert = "4. N-Gabe"
    first_base_fert = "1. Grundd."
    second_base_fert = "2. Grundd."
    third_base_fert = "3. Grundd."
    fourth_base_fert = "4. Grundd."
    lime_fert = "Kalkung"
    misc_fert = "Sonstige"


OrganicMeasureType: enum.Enum = enum.Enum(
    "OrganicMeasureType", [(e.name, e.value) for e in MeasureType if "org_" in e.name]
)
MineralMeasureType: enum.Enum = enum.Enum(
    "MineralMeasureType", [(e.name, e.value) for e in MeasureType if "org_" not in e.name]
)

NMeasureType: enum.Enum = enum.Enum(
    "MeasureType", [(e.name, e.value) for e in MeasureType if e.name.endswith("n_fert")]
)
BasicMeasureType: enum.Enum = enum.Enum(
    "BasicMeasureType", [(e.name, e.value) for e in MeasureType if e.name.endswith("base_fert")]
)
MiscMeasureType: enum.Enum = enum.Enum(
    "MiscMeasureType", [MeasureType.misc_fert.name, MeasureType.misc_fert.value]
)
LimeMeasureType: enum.Enum = enum.Enum(
    "LimeMeasureType", [MeasureType.lime_fert.name, MeasureType.lime_fert.value]
)


class UnitType(enum.Enum):
    """Units for fertilizer and fruit: `dt`, `to` and `cbm`"""

    dt = "dt"
    to = "to"
    cbm = "m³"


class DemandType(enum.Enum):
    """Demand types for fertilization calculation: `removal` and `demand`"""

    removal = "Abfuhr"
    demand = "Bedarf"


class NminType(enum.Enum):
    """Depths to which fruits converts mineral nitrogen."""

    nmin_0 = "0cm"
    nmin_30 = "30cm"
    nmin_60 = "60cm"
    nmin_90 = "90cm"


class NutrientType(enum.Enum):
    """Six important nutrients for fruits and the soil"""

    n = "N"
    p2o5 = "P2O5"
    k2o = "K2O"
    mgo = "MgO"
    s = "S"
    cao = "CaO"
    nh4 = "NH4-N"


class SoilClass(str, enum.Enum):
    """Five levels of nutrient saturated soil"""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
