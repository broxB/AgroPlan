import enum

__all__ = [
    "FieldType",
    "SoilType",
    "HumusType",
    "CropType",
    "CropClass",
    "CultivationType",
    "CutTiming",
    "ResidueType",
    "LegumeType",
    "FertClass",
    "FertType",
    "MeasureType",
    "NminType",
    "UnitType",
    "DemandType",
]


class FieldType(enum.Enum):
    """Field types: `cropland`, `fallow_grassland`, `exchanged_land` etc."""

    grassland = "Grünland"
    cropland = "Ackerland"
    exchanged_land = "Tauschfläche"
    fallow_grassland = "Grünland-Brache"
    fallow_cropland = "Ackerland-Brache"


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


MainCropType: enum.Enum = enum.Enum(
    "MainCropType", [(e.name, e.value) for e in CropType if e.name in "main_"]
)
CatchCropType: enum.Enum = enum.Enum(
    "CatchCropType", [(e.name, e.value) for e in CropType if e.name in "main_"]
)


class CultivationType(enum.Enum):
    """Cultivation classes for crop rotation: `main_crop` etc."""

    catch_crop = "Zwischenfrucht"
    main_crop = "Hauptfrucht"
    second_main_crop = "Zweite Hauptfrucht"
    second_crop = "Zweitfrucht"


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
    catch_not_frozen_fall = "nicht abgf., eing. Herbst"
    catch_not_frozen_spring = "nicht abgf., eing. Frühjahr"
    catch_used = "mit Nutzung"


MainCropResidueType: enum.Enum = enum.Enum(
    "MainCropResidueType", [(e.name, e.value) for e in ResidueType if e.name in "main_"]
)
CatchCropResidueType: enum.Enum = enum.Enum(
    "CatchCropResidueType", [(e.name, e.value) for e in ResidueType if e.name in "catch_"]
)


class LegumeType(enum.Enum):
    """Ratio of legumes in fruits: `grass_less_10`, `crop_10`, `catch_25` etc."""

    # Grünland
    grass_less_5 = "< 5%"
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
    none = "0%"


GrasslandLegumeType: enum.Enum = enum.Enum(
    "GrasslandLegumeType", [(e.name, e.value) for e in LegumeType if e.name in "grass_"]
)
MainCropLegumeType: enum.Enum = enum.Enum(
    "MainCropLegumeType", [(e.name, e.value) for e in LegumeType if e.name in "main_"]
)
CatchCropLegumeType: enum.Enum = enum.Enum(
    "CatchCropLegumeType", [(e.name, e.value) for e in LegumeType if e.name in "catch_"]
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


def find_nmin_type(nmin: int) -> NminType:
    match nmin:
        case 0:
            return NminType.nmin_0
        case 30:
            return NminType.nmin_30
        case 60:
            return NminType.nmin_60
        case 90:
            return NminType.nmin_90
        case _:
            raise ValueError("Invalid Nmin value.")


def find_crop_class(cultivation_type: CultivationType) -> CultivationType:
    match cultivation_type:
        case CultivationType.main_crop | CultivationType.second_main_crop:
            return CropClass.main_crop
        case CultivationType.catch_crop:
            return CropClass.catch_crop
        case CultivationType.second_crop:
            return CropClass.second_crop
        case _:
            raise ValueError(f"Invalid cultivation type passed: {cultivation_type}")
