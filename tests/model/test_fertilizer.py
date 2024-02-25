from decimal import Decimal

import pytest

import app.database.model as db
from app.database.types import FertClass, FertType, FieldType
from app.model.fertilizer import Fertilizer, Mineral, Organic, create_fertilizer


def test_create_fertilizer(
    organic_fertilizer: db.Fertilizer, mineral_fertilizer: db.Fertilizer, guidelines
):
    org_fertilizer = create_fertilizer(organic_fertilizer, guidelines=guidelines)
    assert isinstance(org_fertilizer, Fertilizer)
    assert isinstance(org_fertilizer, Organic)
    assert "Org" in str(org_fertilizer.__repr__)
    assert org_fertilizer.fert_class is FertClass.organic
    min_fertilizer = create_fertilizer(mineral_fertilizer, guidelines=guidelines)
    assert isinstance(min_fertilizer, Mineral)
    assert "Min" in str(min_fertilizer.__repr__)
    assert min_fertilizer.fert_class is FertClass.mineral


@pytest.fixture
def test_fertilizer(organic_fertilizer: db.Fertilizer) -> Fertilizer:
    return Fertilizer(organic_fertilizer)


def test_is_class(test_fertilizer: Fertilizer):
    test_fertilizer.fert_class = FertClass.organic
    assert test_fertilizer.is_class(FertClass.organic) is True
    assert test_fertilizer.is_class(FertClass.mineral) is False
    test_fertilizer.fert_class = FertClass.mineral
    assert test_fertilizer.is_class(FertClass.mineral) is True
    assert test_fertilizer.is_class(FertClass.organic) is False


def test_is_fert_class(test_fertilizer: Fertilizer):
    test_fertilizer.fert_class = FertClass.organic
    assert test_fertilizer.is_organic is True
    assert test_fertilizer.is_mineral is False
    test_fertilizer.fert_class = FertClass.mineral
    assert test_fertilizer.is_mineral is True
    assert test_fertilizer.is_organic is False


def test_is_lime(test_fertilizer: Fertilizer):
    test_fertilizer.fert_type = FertType.lime
    assert test_fertilizer.is_lime is True
    test_fertilizer.fert_type = FertType.n
    assert test_fertilizer.is_lime is False


def test_lime_starvation(test_fertilizer: Fertilizer):
    test_fertilizer.cao = 1
    test_fertilizer.mgo = 1
    test_fertilizer.k2o = 1
    test_fertilizer.p2o5 = 1
    test_fertilizer.s = 1
    test_fertilizer.n = 1
    assert test_fertilizer.lime_starvation(FieldType.cropland) == Decimal("-0.15")
    assert test_fertilizer.lime_starvation(FieldType.grassland) == Decimal("0.05")


@pytest.fixture
def test_organic(organic_fertilizer: db.Fertilizer, guidelines) -> Organic:
    return Organic(organic_fertilizer, guidelines=guidelines)


def test_organic__storage_loss(test_organic: Organic):
    assert test_organic._storage_loss() == Decimal("0.5")


def test_organic_n_total(test_organic: Organic):
    test_organic.n = 100
    assert test_organic.n_total(netto=True) == 50
    assert test_organic.n_total() == 100


def test_organic__factor(test_organic: Organic):
    assert test_organic._factor(FieldType.cropland) == Decimal("0.6")
    assert test_organic._factor(FieldType.grassland) == Decimal("0.5")
    with pytest.raises(KeyError):
        assert test_organic._factor(FieldType.fallow_cropland)
        assert test_organic._factor(FieldType.fallow_grassland)
        assert test_organic._factor(FieldType.exchanged_land)


def test_organic_n_verf(test_organic: Organic):
    test_organic.n = 100
    test_organic.nh4 = 40
    assert test_organic.n_verf(FieldType.cropland) == 60
    assert test_organic.n_verf(FieldType.grassland) == 50
    assert test_organic.n_verf(FieldType.fallow_cropland) == 0
    assert test_organic.n_verf(FieldType.fallow_grassland) == 0
    assert test_organic.n_verf(FieldType.exchanged_land) == 0


def test_organic_lime_starvation(test_organic: Organic):
    test_organic.cao = 1
    test_organic.mgo = 1
    test_organic.k2o = 1
    test_organic.p2o5 = 1
    test_organic.s = 1
    test_organic.n = 1
    assert test_organic.lime_starvation(FieldType.cropland) == Decimal("1.32")
    assert test_organic.lime_starvation(FieldType.grassland) == Decimal("1.52")
    test_organic.fert_type = FertType.org_manure
    assert test_organic.lime_starvation(FieldType.grassland) == Decimal("0.75")


@pytest.fixture
def test_mineral(mineral_fertilizer: db.Fertilizer) -> Mineral:
    return Mineral(mineral_fertilizer)


def test_mineral__n_verf(test_mineral: Mineral):
    test_mineral.n = 123
    test_mineral.nh4 = 321
    assert test_mineral.n_verf() == 321


def test_mineral_n_total(test_mineral: Mineral):
    test_mineral.n = 123
    assert test_mineral.n_total() == 123
