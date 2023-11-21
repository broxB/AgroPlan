import pytest

import app.database.model as db
from app.database.types import (
    CropType,
    CultivationType,
    DemandType,
    LegumeType,
    NminType,
    ResidueType,
)
from app.model import Balance, Crop
from app.model.cultivation import (
    CatchCrop,
    Cultivation,
    MainCrop,
    SecondCrop,
    create_cultivation,
)


@pytest.fixture
def test_crop(crop) -> Crop:
    return Crop(crop)


def test_create_cultivation(cultivation: db.Cultivation, test_crop: Crop):
    cultivation.cultivation_type = CultivationType.main_crop
    main_cult = create_cultivation(cultivation, test_crop)
    assert isinstance(main_cult, MainCrop)
    assert "Main crop" in str(main_cult.__repr__)
    cultivation.cultivation_type = CultivationType.catch_crop
    catch_cult = create_cultivation(cultivation, test_crop)
    assert isinstance(catch_cult, CatchCrop)
    assert "Catch crop" in str(catch_cult.__repr__)
    cultivation.cultivation_type = CultivationType.second_crop
    second_cult = create_cultivation(cultivation, test_crop)
    assert isinstance(second_cult, SecondCrop)
    assert "Second crop" in str(second_cult.__repr__)


@pytest.fixture
def test_cultivation(cultivation, test_crop) -> Cultivation:
    return Cultivation(cultivation, test_crop)


def test_demand(test_cultivation: Cultivation):
    assert test_cultivation.demand(DemandType.demand) == Balance(
        "Crop needs", -110, -154, -154, -154, -20, -0
    )
    assert test_cultivation.demand(DemandType.removal) == Balance(
        "Crop needs", -110, -110, -110, -110, -20, -0
    )
    test_cultivation.residues = ResidueType.main_removed
    assert test_cultivation.demand(DemandType.removal) == Balance(
        "Crop needs", -110, -154, -154, -154, -20, -0
    )
    assert test_cultivation.demand(DemandType.demand, negative_output=False) == Balance(
        "Crop needs",
        110,
        154,
        154,
        154,
        20,
        0,
    )


def test_pre_crop_effect(test_cultivation: Cultivation):
    assert test_cultivation.pre_crop_effect() == 10


def test_legume_delivery_cropland(test_cultivation: Cultivation):
    test_cultivation.legume_rate = LegumeType.none
    assert test_cultivation.legume_delivery() == 0


@pytest.mark.parametrize(
    "legume_rate, expected",
    [
        (LegumeType.grass_less_5, 0),
        (LegumeType.grass_less_10, 20),
        (LegumeType.grass_less_20, 40),
        (LegumeType.grass_greater_20, 60),
    ],
)
def test_legume_delivery_grassland(test_cultivation: Cultivation, legume_rate, expected):
    test_cultivation.crop_type = CropType.permanent_grassland
    test_cultivation.legume_rate = legume_rate
    assert test_cultivation.legume_delivery() == expected


@pytest.mark.parametrize(
    "legume_rate, expected",
    [
        (LegumeType.main_crop_10, 30),
        (LegumeType.main_crop_30, 90),
        (LegumeType.main_crop_60, 180),
        (LegumeType.main_crop_90, 270),
        (LegumeType.none, 0),
    ],
)
def test_legume_delivery_alfalfa_clover_grass(
    test_cultivation: Cultivation, legume_rate, expected
):
    test_cultivation.legume_rate = legume_rate
    test_cultivation.crop_type = CropType.alfalfa_grass
    assert test_cultivation.legume_delivery() == expected
    test_cultivation.crop_type = CropType.clover_grass
    assert test_cultivation.legume_delivery() == expected


def test_legume_delivery_alfalfa_clover(test_cultivation: Cultivation):
    test_cultivation.crop_type = CropType.alfalfa
    assert test_cultivation.legume_delivery() == 360
    test_cultivation.crop_type = CropType.clover
    assert test_cultivation.legume_delivery() == 360


def test_legume_delivery_not_feedable(test_cultivation: Cultivation):
    test_cultivation.crop.feedable = False
    assert test_cultivation.legume_delivery() == 0
    test_cultivation.crop.feedable = True
    test_cultivation.crop_type = CropType.field_grass
    test_cultivation.legume_rate = LegumeType.main_crop_20
    assert test_cultivation.legume_delivery() == 0


def test_reduction(test_cultivation: Cultivation):
    assert test_cultivation.reduction() == 0


def test_is_class(test_cultivation: Cultivation):
    test_cultivation.cultivation_type = CultivationType.main_crop
    assert test_cultivation.is_class(CultivationType.main_crop)


@pytest.fixture
def main_crop(cultivation, test_crop) -> MainCrop:
    cultivation.cultivation_type = CultivationType.main_crop
    return MainCrop(cultivation, test_crop)


@pytest.mark.parametrize(
    "nmin_depth, expected",
    [(NminType.nmin_0, 0), (NminType.nmin_30, 10), (NminType.nmin_60, 20), (NminType.nmin_90, 25)],
)
def test_main_crop_reduction_nmin(main_crop: MainCrop, nmin_depth, expected):
    main_crop.crop.feedable = False
    main_crop.nmin_depth = nmin_depth
    assert main_crop.reduction_nmin() == expected


def test_main_crop_reduction_nmin_without_parametrize(main_crop: MainCrop):
    assert main_crop.reduction_nmin() == 0


def test_main_crop_reduction(main_crop: MainCrop):
    assert main_crop.reduction() == 0
    main_crop.crop.feedable = False
    assert main_crop.reduction() == 0
    # check ackergras für legume delivery


@pytest.fixture
def second_crop(cultivation, test_crop) -> SecondCrop:
    cultivation.cultivation_type = CultivationType.second_crop
    return SecondCrop(cultivation, test_crop)


def test_second_crop_reduction(second_crop: SecondCrop):
    assert second_crop.reduction() == 0
    second_crop.crop.feedable = False
    assert second_crop.reduction() == 0
    # check ackergras für legume delivery


@pytest.fixture
def catch_crop(cultivation, test_crop) -> CatchCrop:
    cultivation.cultivation_type = CultivationType.catch_crop
    return CatchCrop(cultivation, test_crop)


def test_catch_crop_demand(catch_crop: CatchCrop):
    assert catch_crop.demand() == Balance("Crop demand", -60, 0, 0, 0, 0, 0)
    assert catch_crop.demand(negative_output=False) == Balance("Crop demand", 60, 0, 0, 0, 0, 0)


@pytest.mark.parametrize(
    "residues, expected",
    [
        (ResidueType.catch_frozen, 10),
        (ResidueType.catch_not_frozen_spring, 40),
        (ResidueType.catch_not_frozen_fall, 10),
        (ResidueType.catch_used, 10),
    ],
    ids=["frozen", "not frozen, spring", "not frozen fall", "used"],
)
def test_catch_crop_pre_crop_effect(catch_crop: CatchCrop, residues, expected):
    catch_crop.crop_type = CropType.catch_legume
    catch_crop.residues = residues
    assert catch_crop.pre_crop_effect() == expected
