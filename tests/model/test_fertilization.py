import pytest

import app.database.model as db
from app.database.types import CultivationType, FertClass, FieldType, MeasureType
from app.model.fertilization import Fertilization
from app.model.fertilizer import Organic


@pytest.fixture
def test_fertilizer(organic_fertilizer: db.Fertilizer, guidelines) -> Organic:
    return Organic(organic_fertilizer, guidelines=guidelines)


@pytest.fixture
def test_fertilization(
    organic_fertilization: db.Fertilization, test_fertilizer: Organic
) -> Fertilization:
    return Fertilization(
        fertilization=organic_fertilization,
        fertilizer=test_fertilizer,
        crop_feedable=False,
        cultivation_type=CultivationType.main_crop,
    )


def test_fertilization_init(
    test_fertilization: Fertilization,
    test_fertilizer: Organic,
    organic_fertilization: db.Fertilization,
):
    assert isinstance(test_fertilization, Fertilization)
    assert test_fertilization.fertilizer == test_fertilizer
    assert test_fertilization._crop_feedable is False
    assert test_fertilization.cultivation_type == CultivationType.main_crop
    assert test_fertilization.amount == organic_fertilization.amount
    assert test_fertilization.measure is organic_fertilization.measure
    assert CultivationType.main_crop.name in str(test_fertilization.__repr__)


def test_n_total(test_fertilization: Fertilization):
    test_fertilization.fertilizer.n = 10
    assert test_fertilization.n_total(None, None, False) == 100
    assert test_fertilization.n_total(None, None, True) == 50
    test_fertilization.measure = MeasureType.org_fall
    test_fertilization.cultivation_type = CultivationType.main_crop
    assert (
        test_fertilization.n_total(MeasureType.org_spring, CultivationType.main_crop, netto=False)
        == 0
    )
    assert (
        test_fertilization.n_total(MeasureType.org_fall, CultivationType.main_crop, netto=False)
        == 100
    )
    assert (
        test_fertilization.n_total(MeasureType.org_fall, CultivationType.main_crop, netto=True)
        == 50
    )
    assert (
        test_fertilization.n_total(MeasureType.org_fall, CultivationType.catch_crop, netto=False)
        == 100
    )
    test_fertilization.fertilizer.fert_class = FertClass.mineral
    assert (
        test_fertilization.n_total(MeasureType.org_fall, CultivationType.main_crop, netto=False)
        == 0
    )


def test_nutrients(test_fertilization: Fertilization):
    assert (
        test_fertilization.nutrients(FieldType.cropland).p2o5
        == test_fertilization.amount * test_fertilization.fertilizer.p2o5
    )


def test__n_verf(test_fertilization: Fertilization):
    test_fertilization._crop_feedable = False
    assert test_fertilization._n_verf(FieldType.cropland) == test_fertilization.fertilizer.n_verf(
        FieldType.cropland
    )
    assert test_fertilization._n_verf(FieldType.grassland) == test_fertilization.fertilizer.n_verf(
        FieldType.grassland
    )
    test_fertilization._crop_feedable = True
    assert test_fertilization._n_verf(FieldType.cropland) == test_fertilization.fertilizer.n_verf(
        FieldType.grassland
    )
