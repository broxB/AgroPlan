from decimal import Decimal

import pytest

import app.database.model as db
from app.model import Balance, Crop


@pytest.fixture
def crop(field_grass: db.Crop, guidelines) -> Crop:
    return Crop(field_grass, guidelines=guidelines())


def test_demand_crop(crop: Crop):
    assert crop.demand_crop(1, 1) == Balance("", 1, 1, 1, 1, 20, 0)


def test_demand_byproduct(crop: Crop):
    assert crop.demand_byproduct(1) == Balance("", 0, 1, 1, 1, 0, 0)


def test_s_demand(crop: Crop):
    crop.name = "Ackergras 3 Schnitte"
    assert crop.s_demand == 20
    crop.name = "Unsinn"
    assert crop.s_demand == 0


@pytest.mark.parametrize(
    "crop_yield, crop_protein, expected",
    [
        (Decimal("1"), Decimal("1"), Decimal("1")),
        (Decimal("2"), Decimal("1"), Decimal("2")),
        (Decimal("0.5"), Decimal("1"), Decimal("0.5")),
        (Decimal("1"), Decimal("2"), Decimal("2")),
        (Decimal("1"), Decimal("0.5"), Decimal("0.5")),
    ],
    ids=["normal", "higher yield", "lower yield", "higher protein", "lower protein"],
)
def test__n_demand(crop: Crop, crop_yield, crop_protein, expected):
    assert crop._n_demand(crop_yield, crop_protein) == expected


def test__nutrient(crop: Crop):
    assert crop._nutrient(1, Decimal("0.9")) == Decimal("0.9")


def test__nutrient_byproduct(crop: Crop):
    crop.byp_ratio = 1
    assert crop._nutrient_byproduct(1, Decimal("0.9")) == Decimal("0.9")
