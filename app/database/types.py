import enum

__all__ = [
    "FieldType",
    "SoilType",
    "HumusType",
    "CropType",
    "CropClass",
    "RemainsType",
    "FertClass",
    "FertType",
    "MeasureType",
]


class FieldType(enum.Enum):
    grassland = "Grünland"
    cropland = "Ackerland"
    exchanged_land = "Tauschfläche"
    fallow_grassland = "Ackerland-Brache"
    fallow_cropland = "Grünland-Brache"


class SoilType(enum.Enum):
    sand = "Sand"
    light_loamy_sand = "schwach lehmiger Sand"
    strong_loamy_sand = "stark lehmiger Sand"
    sandy_to_silty_loam = "sand. bis schluff. Lehm"
    clayey_loam_to_clay = "toniger Lehm bis Ton"
    moor = "Niedermoor"


class HumusType(enum.Enum):
    less_4 = r"< 4%"
    less_8 = r"4% bis < 8%"
    less_15 = r"8% bis < 15%"
    less_30 = r"15% bis < 30%"
    more_30 = r">= 30%"


class CropType(enum.Enum):
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
    catch_crop = "Zwischenfrucht"
    main_crop = "Hauptfrucht"
    second_crop = "Zweitfrucht"
    first_cut = "1. Schnitt"
    second_cut = "2. Schnitt"
    third_cut = "3. Schnitt"
    fourth_cut = "4. Schnitt"


class RemainsType(enum.Enum):
    # Hauptfrüchte
    remains = "verbleibt"
    no_remains = "abgefahren"
    # Zwischenfrüchte
    frozen = "abgefroren"
    not_frozen_fall = "nicht abgf., eing. Herbst"
    not_frozen_spring = "nicht abgf., eing. Frühjahr"


class FertClass(enum.Enum):
    organic = "Wirtschaftsdünger"
    mineral = "Mineraldünger"


class FertType(enum.Enum):
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
