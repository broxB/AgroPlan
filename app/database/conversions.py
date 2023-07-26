from .types import *


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


def find_crop_class(cultivation_type: CultivationType) -> CropClass:
    match cultivation_type:
        case CultivationType.main_crop | CultivationType.second_main_crop:
            return CropClass.main_crop
        case CultivationType.catch_crop:
            return CropClass.catch_crop
        case CultivationType.second_crop:
            return CropClass.second_crop
        case _:
            raise TypeError(f"Invalid cultivation type passed: {cultivation_type}")


def find_legume_type(cultivation_type: CultivationType) -> LegumeType:
    match cultivation_type:
        case CultivationType.main_crop | CultivationType.second_main_crop:
            return MainCropLegumeType
        case CultivationType.catch_crop:
            return CatchCropLegumeType
        case CultivationType.second_crop:
            return LegumeType
        case _:
            raise TypeError(f"Invalid cultivation type passed: {cultivation_type}")


def find_residue_type(cultivation_type: CultivationType) -> ResidueType:
    match cultivation_type:
        case CultivationType.main_crop | CultivationType.second_main_crop:
            return MainCropResidueType
        case CultivationType.catch_crop:
            return CatchCropResidueType
        case CultivationType.second_crop:
            return ResidueType
        case _:
            raise TypeError(f"Invalid cultivation type passed: {cultivation_type}")


def find_min_fert_type(measure_name: str) -> MineralFertType:
    if measure_name not in [e.name for e in MineralMeasureType]:
        raise TypeError(f"{measure_name} has no corresponding MineralFertType.")
    if measure_name in [e.name for e in NMeasureType]:
        return NFertType
    elif measure_name in [e.name for e in BasicMeasureType]:
        return BasicFertType
    elif measure_name in [e.name for e in MiscMeasureType]:
        return MiscFertType
    elif measure_name in [e.name for e in LimeMeasureType]:
        return LimeFertType
    raise TypeError(f"{measure_name} has no corresponding FertType.")


def find_org_fert_type(measure_name: str) -> OrganicFertType:
    if measure_name in [e.name for e in OrganicMeasureType]:
        return OrganicFertType
    raise TypeError(f"{measure_name} has no corresponding OrganicFertType.")
