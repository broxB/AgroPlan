from decimal import Decimal

import pytest

from app.model.crop import Crop


@pytest.fixture
def crop(crop) -> Crop:
    return Crop(crop)


@pytest.mark.parametrize(
    "crop_yield, crop_protein, expected",
    [
        (Decimal("100"), Decimal("16"), [100, 100, 100, 100, 20, 0]),
        (Decimal("110"), Decimal("16.5"), [Decimal("110.75"), 110, 110, 110, 20, 0]),
        (Decimal("90"), Decimal("15.5"), [Decimal("79.25"), 90, 90, 90, 20, 0]),
    ],
)
def test_demand_crop(crop: Crop, crop_yield, crop_protein, expected):
    assert crop.demand_crop(crop_yield, crop_protein) == expected


@pytest.mark.parametrize(
    "crop_yield, expected",
    [
        (Decimal("100"), [0, 40, 40, 40, 0, 0]),
        (Decimal("110"), [0, 44, 44, 44, 0, 0]),
        (Decimal("90"), [0, 36, 36, 36, 0, 0]),
    ],
)
def test_demand_byproduct(crop: Crop, crop_yield, expected):
    assert crop.demand_byproduct(crop_yield) == expected


def test_s_demand(crop: Crop):
    assert crop.s_demand == 20


@pytest.mark.parametrize(
    "crop_yield, crop_protein, expected",
    [
        (Decimal("100"), Decimal("16"), Decimal("100")),
        (Decimal("110"), Decimal("16.5"), Decimal("110.75")),
        (Decimal("90"), Decimal("15.5"), Decimal("79.25")),
    ],
)
def test__n_demand(crop: Crop, crop_yield, crop_protein, expected):
    assert crop._n_demand(crop_yield, crop_protein) == expected


@pytest.mark.parametrize(
    "crop_yield, nutrient, expected",
    [
        (Decimal("100"), Decimal("0.9"), Decimal("90")),
        (Decimal("110"), Decimal("0.9"), Decimal("99")),
        (Decimal("90"), Decimal("0.9"), Decimal("81")),
    ],
)
def test__nutrient(crop: Crop, crop_yield, nutrient, expected):
    assert crop._nutrient(crop_yield, nutrient) == expected


@pytest.mark.parametrize(
    "crop_yield, byp_nutrient, expected",
    [
        (Decimal("100"), Decimal("0.9"), Decimal("72")),
        (Decimal("110"), Decimal("0.9"), Decimal("79.2")),
        (Decimal("90"), Decimal("0.9"), Decimal("64.8")),
    ],
)
def test__nutrient_byproduct(crop: Crop, crop_yield, byp_nutrient, expected):
    assert crop._nutrient_byproduct(crop_yield, byp_nutrient) == expected
