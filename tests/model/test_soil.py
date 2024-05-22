from decimal import Decimal

import pytest

from app.database.model import Field, SoilSample
from app.database.types import FieldType, HumusType, SoilType
from app.model.soil import Soil, create_soil_sample


@pytest.fixture
def empty_guidelines():
    class guidelines:
        @staticmethod
        def soil_reductions():
            return {}

        @staticmethod
        def p2o5_reductions():
            return {}

        @staticmethod
        def k2o_reductions():
            return {}

        @staticmethod
        def mg_reductions():
            return {}

        @staticmethod
        def sulfur_reductions():
            return {}

        @staticmethod
        def cao_reductions():
            return {}

        @staticmethod
        def p2o5_classes():
            return {}

        @staticmethod
        def k2o_classes():
            return {}

        @staticmethod
        def mg_classes():
            return {}

        @staticmethod
        def ph_classes():
            return {}

        @staticmethod
        def org_factor():
            return {}

        @staticmethod
        def pre_crop_effect():
            return {}

        @staticmethod
        def legume_delivery():
            return {}

        @staticmethod
        def sulfur_needs():
            return {}

    return guidelines


def test_create_soil_sample(field_first_year: Field, guidelines, fill_db):
    soil = create_soil_sample(
        field_first_year.soil_samples,
        field_first_year.field_type,
        field_first_year.year,
        guidelines=guidelines,
    )
    assert isinstance(soil, Soil)
    soil = create_soil_sample(
        list(), field_first_year.field_type, field_first_year.year, guidelines=guidelines
    )
    assert soil is None


@pytest.fixture
def soil(soil_sample: SoilSample, field_first_year: Field, guidelines) -> Soil:
    soil_sample.humus = HumusType.less_4
    soil_sample.soil_type = SoilType.sand
    return Soil(soil_sample, field_first_year.field_type, guidelines=guidelines)


@pytest.fixture
def empty_soil(soil_sample: SoilSample, field_first_year: Field, empty_guidelines) -> Soil:
    soil_sample.humus = HumusType.less_4
    soil_sample.soil_type = SoilType.sand
    return Soil(soil_sample, field_first_year.field_type, guidelines=empty_guidelines)


@pytest.mark.parametrize(
    "field_type, expected", [(FieldType.cropland, 0), (FieldType.grassland, 10)]
)
def test_reduction_n(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.reduction_n() == expected


def test_reduction_n_error(empty_soil: Soil):
    assert empty_soil.reduction_n() == 0


@pytest.mark.parametrize(
    "field_type, expected", [(FieldType.cropland, -69), (FieldType.grassland, -46)]
)
def test_reduction_p2o5(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.reduction_p2o5() == expected


def test_reduction_p2o5_none_value(soil: Soil):
    soil.p2o5 = None
    assert soil.reduction_p2o5() == Decimal()


def test_reduction_p2o5_error(empty_soil: Soil):
    assert empty_soil.reduction_p2o5() == 0


@pytest.mark.parametrize(
    "field_type, expected", [(FieldType.cropland, -72), (FieldType.grassland, -48)]
)
def test_reduction_k2o(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.reduction_k2o() == expected


def test_reduction_k2o_none_value(soil: Soil):
    soil.k2o = None
    assert soil.reduction_k2o() == Decimal()


def test_reduction_k2o_error(empty_soil: Soil):
    assert empty_soil.reduction_k2o() == 0


@pytest.mark.parametrize(
    "field_type, expected", [(FieldType.cropland, -50), (FieldType.grassland, -50)]
)
def test_reduction_mg(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.reduction_mg() == expected


def test_reduction_mg_none_value(soil: Soil):
    soil.mg = None
    assert soil.reduction_mg() == Decimal()


def test_reduction_mg_error(empty_soil: Soil):
    assert empty_soil.reduction_mg() == 0


@pytest.mark.parametrize(
    "field_type, expected", [(FieldType.cropland, -1125), (FieldType.grassland, -750)]
)
def test_reduction_cao(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.reduction_cao() == expected


def test_reduction_cao_none_value(soil: Soil):
    assert soil.reduction_cao(preservation=True) == -150
    soil.ph = None
    assert soil.reduction_cao() == Decimal()
    soil.ph = Decimal(10)
    assert soil.reduction_cao() == Decimal()


def test_reduction_cao_error(empty_soil: Soil):
    assert empty_soil.reduction_cao() == 0


def test_reduction_s(soil: Soil):
    assert soil.reduction_s(s_demand=Decimal(0), n_total=(0)) == 0


def test_reduction_s_error(empty_soil: Soil):
    assert empty_soil.reduction_s(s_demand=0, n_total=0) == 0


@pytest.mark.parametrize(
    "field_type, expected", [(FieldType.cropland, "A"), (FieldType.grassland, "A")]
)
def test_class_p2o5(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.class_p2o5() == expected


def test_class_p2o5_none_value(soil: Soil):
    soil.p2o5 = None
    assert soil.class_p2o5() == ""


def test_class_p2o5_error(empty_soil: Soil):
    assert empty_soil.class_p2o5() == ""


@pytest.mark.parametrize(
    "field_type, expected", [(FieldType.cropland, "A"), (FieldType.grassland, "A")]
)
def test_class_k2o(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.class_k2o() == expected


def test_class_k2o_none_value(soil: Soil):
    soil.k2o = None
    assert soil.class_k2o() == ""


def test_class_k2o_error(empty_soil: Soil):
    assert empty_soil.class_k2o() == ""


@pytest.mark.parametrize(
    "field_type, expected", [(FieldType.cropland, "A"), (FieldType.grassland, "A")]
)
def test_class_mg(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.class_mg() == expected


def test_class_mg_none_value(soil: Soil):
    soil.mg = None
    assert soil.class_mg() == ""


def test_class_mg_error(empty_soil: Soil):
    assert empty_soil.class_mg() == ""


@pytest.mark.parametrize(
    "field_type, expected", [(FieldType.cropland, "A"), (FieldType.grassland, "A")]
)
def test_class_ph(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.class_ph() == expected


def test_class_ph_none_value(soil: Soil):
    soil.ph = None
    assert soil.class_ph() == ""


def test_class_ph_error(empty_soil: Soil):
    assert empty_soil.class_ph() == ""


@pytest.mark.parametrize(
    "field_type, expected",
    [(FieldType.cropland, Decimal("5.4")), (FieldType.grassland, Decimal("4.7"))],
)
def test_optimal_ph(soil: Soil, field_type, expected):
    soil.field_type = field_type
    assert soil.optimal_ph() == expected


def test_optimal_ph_error(empty_soil: Soil):
    assert empty_soil.optimal_ph() == 0


@pytest.mark.parametrize(
    "values, expected",
    [([0.1, 0.2], [Decimal("0.1"), Decimal("0.2")]), ([0], [Decimal()]), ([], [])],
)
def test_to_decimal(soil: Soil, values, expected):
    assert soil._to_decimal(values) == expected
