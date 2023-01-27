import pytest

from app.database.types import (
    CropClass,
    CultivationType,
    NminType,
    find_crop_class,
    find_nmin_type,
)


def test_find_nmin_type():
    assert find_nmin_type(0) is NminType.nmin_0
    assert find_nmin_type(30) is NminType.nmin_30
    assert find_nmin_type(60) is NminType.nmin_60
    assert find_nmin_type(90) is NminType.nmin_90
    with pytest.raises(ValueError):
        find_nmin_type("0")


def test_find_crop_class():
    assert find_crop_class(CultivationType.main_crop) is CropClass.main_crop
    assert find_crop_class(CultivationType.second_main_crop) is CropClass.main_crop
    assert find_crop_class(CultivationType.catch_crop) is CropClass.catch_crop
    assert find_crop_class(CultivationType.second_crop) is CropClass.second_crop
    with pytest.raises(ValueError):
        find_crop_class("main_crop")
