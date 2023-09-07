from enum import Enum

import pytest

from app.database.types import (
    BaseType,
    BasicFertType,
    CatchCropLegumeType,
    CatchCropResidueType,
    CropClass,
    CultivationType,
    FertClass,
    FertType,
    LegumeType,
    LimeFertType,
    MainCropLegumeType,
    MainCropResidueType,
    MainCultivationType,
    MeasureType,
    MineralFertType,
    MineralMeasureType,
    MiscFertType,
    NFertType,
    NminType,
    OrganicFertType,
    OrganicMeasureType,
    ResidueType,
)


def test_base_type():
    class BaseEnum(BaseType):
        a = "A"
        b = "B"

    SubEnum = Enum("SubEnum", (BaseEnum.a.name, BaseEnum.a.value, "c", "C"))
    assert str(BaseEnum.a) == "A"
    assert BaseEnum.a == "a"
    assert BaseEnum.a == BaseEnum.a
    assert BaseEnum.a is BaseEnum.a
    assert BaseEnum.a != SubEnum.a
    assert BaseEnum.from_sub_type(SubEnum.a) == BaseEnum.a
    with pytest.raises(KeyError):
        BaseEnum.from_sub_type(SubEnum.C)


def test_cultivation_type_from_crop_class():
    assert CultivationType.from_crop_class(CropClass.main_crop) == MainCultivationType
    assert CultivationType.from_crop_class(CropClass.second_crop) == CultivationType.second_crop
    assert CultivationType.from_crop_class(CropClass.catch_crop) == CultivationType.catch_crop
    with pytest.raises(TypeError):
        CultivationType.from_crop_class(CultivationType.main_crop)


def test_crop_class_from_cultivation():
    assert CropClass.from_cultivation(CultivationType.main_crop) == CropClass.main_crop
    assert CropClass.from_cultivation(CultivationType.second_main_crop) == CropClass.main_crop
    assert CropClass.from_cultivation(CultivationType.catch_crop) == CropClass.catch_crop
    assert CropClass.from_cultivation(CultivationType.second_crop) == CropClass.second_crop
    with pytest.raises(TypeError):
        CropClass.from_cultivation(CropClass.main_crop)


def test_residue_type_from_cultivation():
    assert ResidueType.from_cultivation(CultivationType.main_crop) == MainCropResidueType
    assert ResidueType.from_cultivation(CultivationType.second_main_crop) == MainCropResidueType
    assert ResidueType.from_cultivation(CultivationType.catch_crop) == CatchCropResidueType
    assert ResidueType.from_cultivation(CultivationType.second_crop) == ResidueType
    with pytest.raises(TypeError):
        ResidueType.from_cultivation(CropClass.main_crop)


def test_legume_type_from_cultivation():
    assert LegumeType.from_cultivation(CultivationType.main_crop) == MainCropLegumeType
    assert LegumeType.from_cultivation(CultivationType.second_main_crop) == MainCropLegumeType
    assert LegumeType.from_cultivation(CultivationType.catch_crop) == CatchCropLegumeType
    assert LegumeType.from_cultivation(CultivationType.second_crop) == LegumeType
    with pytest.raises(TypeError):
        LegumeType.from_cultivation(CropClass.main_crop)


def test_fert_type_from_measure():
    assert FertType.from_measure(MeasureType.first_first_n_fert) == NFertType
    assert FertType.from_measure(MeasureType.first_n_fert) == NFertType
    assert FertType.from_measure(MeasureType.first_base_fert) == BasicFertType
    assert FertType.from_measure(MeasureType.lime_fert) == LimeFertType
    assert FertType.from_measure(MeasureType.misc_fert) == MiscFertType
    assert FertType.from_measure(MeasureType.org_fall) == OrganicFertType
    with pytest.raises(TypeError):
        FertType.from_measure(FertClass.mineral)


def test_fert_type_from_fert_class():
    assert FertType.from_fert_class(FertClass.mineral) == MineralFertType
    assert FertType.from_fert_class(FertClass.organic) == OrganicFertType
    with pytest.raises(TypeError):
        FertType.from_fert_class(MeasureType.first_base_fert)


def test_fert_type_is_organic():
    assert FertType.is_organic(OrganicFertType)
    assert FertType.is_organic(MineralFertType) is False


def test_fert_type_is_mineral():
    assert FertType.is_mineral(MineralFertType)
    assert FertType.is_mineral(NFertType)
    assert FertType.is_mineral(BasicFertType)
    assert FertType.is_mineral(MineralFertType)
    assert FertType.is_mineral(OrganicFertType) is False


def test_measure_type_from_fert_class():
    assert MeasureType.from_fert_class(FertClass.mineral) == MineralMeasureType
    assert MeasureType.from_fert_class(FertClass.organic) == OrganicMeasureType
    with pytest.raises(TypeError):
        MeasureType.from_fert_class(FertType.misc)


def test_nmin_type_from_int():
    assert NminType.from_int(0) == NminType.nmin_0
    assert NminType.from_int(30) == NminType.nmin_30
    assert NminType.from_int(60) == NminType.nmin_60
    assert NminType.from_int(90) == NminType.nmin_90
    with pytest.raises(TypeError):
        NminType.from_int("0")
