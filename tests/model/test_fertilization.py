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


@pytest.mark.parametrize(
    "measure, cultivation_type, expected",
    [
        (
            MeasureType.org_fall,
            CultivationType.catch_crop,
            [100, 0, 100, 0, 0, 100, 0, 0, 0, 0, 0],
        ),
        (
            MeasureType.org_spring,
            CultivationType.catch_crop,
            [0, 100, 100, 0, 0, 0, 100, 0, 0, 0, 0],
        ),
        (MeasureType.org_fall, CultivationType.main_crop, [100, 0, 0, 100, 0, 0, 0, 100, 0, 0, 0]),
        (
            MeasureType.org_spring,
            CultivationType.main_crop,
            [0, 100, 0, 100, 0, 0, 0, 0, 100, 0, 0],
        ),
        (
            MeasureType.org_fall,
            CultivationType.second_crop,
            [100, 0, 0, 0, 100, 0, 0, 0, 0, 100, 0],
        ),
        (
            MeasureType.org_spring,
            CultivationType.second_crop,
            [0, 100, 0, 0, 100, 0, 0, 0, 0, 0, 100],
        ),
    ],
)
def test_n_total(
    test_fertilization: Fertilization,
    measure: MeasureType,
    cultivation_type: CultivationType,
    expected,
):
    test_fertilization.amount = 10
    test_fertilization.fertilizer.n = 10
    test_fertilization.fertilizer.fert_class = FertClass.organic
    test_fertilization.measure = measure
    test_fertilization.cultivation_type = cultivation_type
    assert test_fertilization.n_total(MeasureType.org_fall, None, False) == expected[0]
    assert test_fertilization.n_total(MeasureType.org_spring, None, False) == expected[1]
    assert test_fertilization.n_total(None, CultivationType.catch_crop, False) == expected[2]
    assert test_fertilization.n_total(None, CultivationType.main_crop, False) == expected[3]
    assert test_fertilization.n_total(None, CultivationType.second_crop, False) == expected[4]
    assert (
        test_fertilization.n_total(MeasureType.org_fall, CultivationType.catch_crop, False)
        == expected[5]
    )
    assert (
        test_fertilization.n_total(MeasureType.org_spring, CultivationType.catch_crop, False)
        == expected[6]
    )
    assert (
        test_fertilization.n_total(MeasureType.org_fall, CultivationType.main_crop, False)
        == expected[7]
    )
    assert (
        test_fertilization.n_total(MeasureType.org_spring, CultivationType.main_crop, False)
        == expected[8]
    )
    assert (
        test_fertilization.n_total(MeasureType.org_fall, CultivationType.second_crop, False)
        == expected[9]
    )
    assert (
        test_fertilization.n_total(MeasureType.org_spring, CultivationType.second_crop, False)
        == expected[10]
    )


def test_n_total_mineral(test_fertilization: Fertilization):
    test_fertilization.amount = 10
    test_fertilization.fertilizer.n = 10
    test_fertilization.fertilizer.fert_class = FertClass.mineral
    assert test_fertilization.n_total(None, None, False) == 0


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
