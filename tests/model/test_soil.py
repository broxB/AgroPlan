from decimal import Decimal

import pytest

from app.database.model import Field, SoilSample
from app.database.types import FieldType
from app.model.soil import Soil, create_soil_sample


def test_create_soil_sample(field: Field, soil_sample: SoilSample):
    soil = create_soil_sample(field.soil_samples, field.field_type, field.year)
    assert isinstance(soil, Soil)
    soil = create_soil_sample(list(), field.field_type, field.year)
    assert soil is None


@pytest.fixture
def soil(soil_sample: SoilSample, field: Field) -> Soil:
    return Soil(soil_sample, field.field_type)


@pytest.mark.parametrize(
    "field_type, expected",
    [(FieldType.cropland, 20), (FieldType.grassland, 10)],
)
def test_reduction_n(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.reduction_n() == expected


@pytest.mark.parametrize(
    "field_type, expected",
    [(FieldType.cropland, -69), (FieldType.grassland, -46)],
)
def test_reduction_p2o5(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.reduction_p2o5() == expected


def test_reduction_p2o5_without_parametrize(soil: Soil):
    soil.p2o5 = None
    assert soil.reduction_p2o5() == Decimal()


@pytest.mark.parametrize(
    "field_type, expected",
    [(FieldType.cropland, -72), (FieldType.grassland, -48)],
)
def test_reduction_k2o(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.reduction_k2o() == expected


def test_reduction_k2o_without_parametrize(soil: Soil):
    soil.k2o = None
    assert soil.reduction_k2o() == Decimal()


@pytest.mark.parametrize(
    "field_type, expected",
    [(FieldType.cropland, -50), (FieldType.grassland, -50)],
)
def test_reduction_mg(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.reduction_mg() == expected


def test_reduction_mg_without_parametrize(soil: Soil):
    soil.mg = None
    assert soil.reduction_mg() == Decimal()


@pytest.mark.parametrize(
    "field_type, expected",
    [(FieldType.cropland, -1250), (FieldType.grassland, -750)],
)
def test_reduction_cao(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.reduction_cao() == expected


def test_reduction_cao_without_parametrize(soil: Soil):
    assert soil.reduction_cao(preservation=True) == -125
    soil.ph = None
    assert soil.reduction_cao() == Decimal()
    soil.ph = Decimal(10)
    assert soil.reduction_cao() == Decimal()


def test_reduction_s(soil: Soil):
    assert soil.reduction_s(s_demand=Decimal(0), n_total=(0)) == 0


@pytest.mark.parametrize(
    "field_type, expected",
    [(FieldType.cropland, "A"), (FieldType.grassland, "A")],
)
def test_class_p2o5(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.class_p2o5() == expected


def test_class_p2o5_without_parametrize(soil: Soil):
    soil.p2o5 = None
    assert soil.class_p2o5() == ""


@pytest.mark.parametrize(
    "field_type, expected",
    [(FieldType.cropland, "A"), (FieldType.grassland, "A")],
)
def test_class_k2o(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.class_k2o() == expected


def test_class_k2o_without_parametrize(soil: Soil):
    soil.k2o = None
    assert soil.class_k2o() == ""


@pytest.mark.parametrize(
    "field_type, expected",
    [(FieldType.cropland, "A"), (FieldType.grassland, "A")],
)
def test_class_mg(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.class_mg() == expected


def test_class_mg_without_parametrize(soil: Soil):
    soil.mg = None
    assert soil.class_mg() == ""


@pytest.mark.parametrize(
    "field_type, expected",
    [(FieldType.cropland, "A"), (FieldType.grassland, "A")],
)
def test_class_ph(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.class_ph() == expected


def test_class_ph_without_parametrize(soil: Soil):
    soil.ph = None
    assert soil.class_ph() == ""


@pytest.mark.parametrize(
    "field_type, expected",
    [(FieldType.cropland, Decimal("5")), (FieldType.grassland, Decimal("4.7"))],
)
def test_optimal_ph(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.optimal_ph() == expected


@pytest.mark.parametrize(
    "values, expected",
    [([0.1, 0.2], [Decimal("0.1"), Decimal("0.2")]), ([0], [Decimal()]), ([], [])],
)
def test_to_decimal(soil: Soil, values, expected):
    assert soil.to_decimal(values) == expected
