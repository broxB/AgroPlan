from decimal import Decimal

import pytest

import app.database.model as db
from app.model import Balance, Crop


@pytest.fixture
def crop(main_crop: db.Crop, guidelines) -> Crop:
    return Crop(main_crop, guidelines=guidelines())


@pytest.mark.parametrize(
    "crop_yield, crop_protein, expected",
    [
        (Decimal("110"), Decimal("16.5"), Balance("", Decimal("110.75"), 110, 110, 110, 20, 0)),
        (Decimal("100"), Decimal("16"), Balance("", 100, 100, 100, 100, 20, 0)),
        (Decimal("90"), Decimal("15.5"), Balance("", Decimal("79.25"), 90, 90, 90, 20, 0)),
    ],
    ids=["higher yield", "normal yield", "lower yield"],
)
def test_demand_crop(crop: Crop, crop_yield, crop_protein, expected):
    assert crop.demand_crop(crop_yield, crop_protein) == expected


@pytest.mark.parametrize(
    "crop_yield, expected",
    [
        (Decimal("110"), Balance("", 0, 44, 44, 44, 0, 0)),
        (Decimal("100"), Balance("", 0, 40, 40, 40, 0, 0)),
        (Decimal("90"), Balance("", 0, 36, 36, 36, 0, 0)),
    ],
    ids=["higher yield", "normal yield", "lower yield"],
)
def test_demand_byproduct(crop: Crop, crop_yield, expected):
    assert crop.demand_byproduct(crop_yield) == expected


def test_s_demand(crop: Crop):
    assert crop.s_demand == 20
    crop.name = "Unsinn"
    assert crop.s_demand == 0


@pytest.mark.parametrize(
    "crop_yield, crop_protein, expected",
    [
        (Decimal("110"), Decimal("16.5"), Decimal("110.75")),
        (Decimal("100"), Decimal("16"), Decimal("100")),
        (Decimal("90"), Decimal("15.5"), Decimal("79.25")),
    ],
    ids=["higher yield", "normal yield", "lower yield"],
)
def test__n_demand(crop: Crop, crop_yield, crop_protein, expected):
    assert crop._n_demand(crop_yield, crop_protein) == expected


@pytest.mark.parametrize(
    "crop_yield, nutrient, expected",
    [
        (Decimal("110"), Decimal("0.9"), Decimal("99")),
        (Decimal("100"), Decimal("0.9"), Decimal("90")),
        (Decimal("90"), Decimal("0.9"), Decimal("81")),
    ],
    ids=["higher yield", "normal yield", "lower yield"],
)
def test__nutrient(crop: Crop, crop_yield, nutrient, expected):
    assert crop._nutrient(crop_yield, nutrient) == expected


@pytest.mark.parametrize(
    "crop_yield, byp_nutrient, expected",
    [
        (Decimal("110"), Decimal("0.9"), Decimal("79.2")),
        (Decimal("100"), Decimal("0.9"), Decimal("72")),
        (Decimal("90"), Decimal("0.9"), Decimal("64.8")),
    ],
    ids=["higher yield", "normal yield", "lower yield"],
)
def test__nutrient_byproduct(crop: Crop, crop_yield, byp_nutrient, expected):
    assert crop._nutrient_byproduct(crop_yield, byp_nutrient) == expected


def test_repr(crop: Crop):
    assert crop.name in str(crop.__repr__)
