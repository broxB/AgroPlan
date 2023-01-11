import enum

__all__ = [
    "FieldType",
    "SoilType",
    "HumusType",
    "CropType",
    "CropClass",
    "ResidueType",
    "LegumeType",
    "FertClass",
    "FertType",
    "MeasureType",
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
    non_legume = "Nichtleguminosen"
    legume = "Leguminosen"
    other_catch_crop = "andere Zwischenfrüchte"


class CropClass(enum.Enum):
    """Fruit classes for crop rotation: `main_crop` or `first_cut` etc."""

    catch_crop = "Zwischenfrucht"
    main_crop = "Hauptfrucht"
    second_crop = "Zweitfrucht"
    first_cut = "1. Schnitt"
    second_cut = "2. Schnitt"
    third_cut = "3. Schnitt"
    fourth_cut = "4. Schnitt"


class ResidueType(enum.Enum):
    """Crop residues for preceding crop effect: `stayed`, `removed` or `frozen`, `catch_crop_used` etc."""

    # Hauptfrüchte
    stayed = "verbleibt"
    removed = "abgefahren"
    no_residues = None
    # Zwischenfrüchte
    frozen = "abgefroren"
    not_frozen_fall = "nicht abgf., eing. Herbst"
    not_frozen_spring = "nicht abgf., eing. Frühjahr"
    catch_crop_used = "mit Nutzung"


class LegumeType(enum.Enum):
    """Ratio of legumes in fruits: `grass_less_10`, `crop_10`, `catch_25` etc."""

    # Grünland
    grass_less_5 = "< 5%"
    grass_less_10 = r"5% bis 10%"
    grass_less_20 = r"> 10% bis 20%"
    grass_greater_20 = r"> 20%"
    # Ackerland
    crop_0 = r"< 10%"
    crop_10 = r"10% - 19%"
    crop_20 = r"20% - 29%"
    crop_30 = r"30% - 39%"
    crop_40 = r"40% - 49%"
    crop_50 = r"50% - 59%"
    crop_60 = r"60% - 69%"
    crop_70 = r"70% - 79%"
    crop_80 = r"80% - 89%"
    crop_90 = r"90% - 99%"
    crop_100 = r"100%"
    # Zwischenfrucht
    catch_25 = r"< 25%"
    catch_50 = r"25% bis 75%"
    catch_75 = r"> 75%"
    none = "0%"


class FertClass(enum.Enum):
    """Fertilizer basic classifications: `organic` or `mineral`"""

    organic = "Wirtschaftsdünger"
    mineral = "Mineraldünger"


class FertType(enum.Enum):
    """Fertilizer subtype classifications: `slurry`, `digestate` or `n_p_k`, `lime` etc."""

    # organic
    digestate = "Gärrest"
    slurry = "Gülle"
    manure = "Festmist"
    dry_manure = "Trockenkot"
    compost = "Kompost"
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


class MeasureType(enum.Enum):
    """Measures for fertilization: `fall`, `first_n_fert`, `lime_fert` etc."""

    fall = "Herbst"
    spring = "Frühjahr"
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
