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
from app.model.cultivation import CatchCrop, Cultivation, MainCrop, SecondCrop, create_cultivation


@pytest.fixture
def test_crop(field_grass: db.Crop, guidelines) -> Crop:
    return Crop(field_grass, guidelines=guidelines)


def test_create_cultivation(cultivation_field_grass: db.Cultivation, test_crop: Crop, guidelines):
    cultivation_field_grass.cultivation_type = CultivationType.main_crop
    main_cult = create_cultivation(cultivation_field_grass, test_crop, guidelines=guidelines)
    assert isinstance(main_cult, MainCrop)
    assert "Main crop" in str(main_cult.__repr__)
    cultivation_field_grass.cultivation_type = CultivationType.catch_crop
    catch_cult = create_cultivation(cultivation_field_grass, test_crop, guidelines=guidelines)
    assert isinstance(catch_cult, CatchCrop)
    assert "Catch crop" in str(catch_cult.__repr__)
    cultivation_field_grass.cultivation_type = CultivationType.second_crop
    second_cult = create_cultivation(cultivation_field_grass, test_crop, guidelines=guidelines)
    assert isinstance(second_cult, SecondCrop)
    assert "Second crop" in str(second_cult.__repr__)


@pytest.fixture
def test_cultivation(cultivation_field_grass, test_crop, guidelines) -> Cultivation:
    return Cultivation(cultivation_field_grass, test_crop, guidelines=guidelines())


@pytest.mark.parametrize(
    "option_p205, option_k2o, option_mgo, expected",
    [
        (
            DemandType.demand,
            DemandType.demand,
            DemandType.demand,
            Balance("Crop needs", -1, -2, -2, -2, -20, -0),
        ),
        (
            DemandType.removal,
            DemandType.demand,
            DemandType.demand,
            Balance("Crop needs", -1, -1, -2, -2, -20, -0),
        ),
        (
            DemandType.demand,
            DemandType.removal,
            DemandType.demand,
            Balance("Crop needs", -1, -2, -1, -2, -20, -0),
        ),
        (
            DemandType.demand,
            DemandType.demand,
            DemandType.removal,
            Balance("Crop needs", -1, -2, -2, -1, -20, -0),
        ),
    ],
)
def test_demand(test_cultivation: Cultivation, option_p205, option_k2o, option_mgo, expected):
    assert test_cultivation.demand(option_p205, option_k2o, option_mgo) == expected
    assert (
        test_cultivation.demand(option_p205, option_k2o, option_mgo, negative_output=False)
        == expected * -1
    )


def test_demand_no_residue(test_cultivation: Cultivation):
    test_cultivation.residues = ResidueType.main_removed
    assert test_cultivation.demand(
        DemandType.demand, DemandType.demand, DemandType.demand
    ) == Balance("Crop needs", -1, -2, -2, -2, -20, -0)
    assert test_cultivation.demand(
        DemandType.removal, DemandType.removal, DemandType.removal
    ) == Balance("Crop needs", -1, -1, -1, -1, -20, -0)


def test_pre_crop_effect(test_cultivation: Cultivation):
    assert test_cultivation.pre_crop_effect() == 10


def test_legume_delivery_cropland(test_cultivation: Cultivation):
    test_cultivation.legume_rate = LegumeType.none
    assert test_cultivation.legume_delivery() == 0


def test_legume_delivery_grassland(test_cultivation: Cultivation):
    test_cultivation.crop_type = CropType.permanent_grassland
    test_cultivation.legume_rate = LegumeType.grass_less_10
    assert test_cultivation.legume_delivery() == 20


def test_legume_delivery_alfalfa_clover(test_cultivation: Cultivation):
    test_cultivation.crop_type = CropType.alfalfa_grass
    test_cultivation.legume_rate = LegumeType.main_crop_10
    assert test_cultivation.legume_delivery() == 30
    test_cultivation.crop_type = CropType.alfalfa
    assert test_cultivation.legume_delivery() == 360
    # test exception
    test_cultivation.crop_type = CropType.alfalfa_grass
    test_cultivation.legume_rate = LegumeType.none
    assert test_cultivation.legume_delivery() == 0


def test_legume_delivery_not_feedable(test_cultivation: Cultivation):
    test_cultivation.crop.feedable = False
    assert test_cultivation.legume_delivery() == 0
    test_cultivation.crop.feedable = True
    test_cultivation.crop_type = CropType.field_grass
    test_cultivation.legume_rate = LegumeType.main_crop_20
    assert test_cultivation.legume_delivery() == 0


def test_reduction(test_cultivation: Cultivation):
    assert test_cultivation.reduction() == 0


@pytest.fixture
def test_main_crop(cultivation_field_grass, test_crop) -> MainCrop:
    cultivation_field_grass.cultivation_type = CultivationType.main_crop
    return MainCrop(cultivation_field_grass, test_crop)


@pytest.mark.parametrize(
    "nmin_depth, expected",
    [(NminType.nmin_0, 0), (NminType.nmin_30, 1), (NminType.nmin_60, 2), (NminType.nmin_90, 3)],
)
def test_main_crop_reduction_nmin(test_main_crop: MainCrop, nmin_depth, expected):
    test_main_crop.crop.feedable = False
    test_main_crop.nmin_depth = nmin_depth
    assert test_main_crop.reduction_nmin() == expected


def test_main_crop_reduction_nmin_feedable(test_main_crop: MainCrop):
    test_main_crop.crop.feedable = True
    assert test_main_crop.reduction_nmin() == 0


@pytest.fixture
def catch_crop(cultivation_field_grass, test_crop, guidelines) -> CatchCrop:
    cultivation_field_grass.cultivation_type = CultivationType.catch_crop
    return CatchCrop(cultivation_field_grass, test_crop, guidelines=guidelines)


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
