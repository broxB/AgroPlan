from copy import deepcopy
from decimal import Decimal

import pytest

import app.database.model as db
from app.database.types import (
    CultivationType,
    DemandType,
    FertClass,
    FieldType,
    HumusType,
    MeasureType,
)
from app.model.balance import Balance
from app.model.crop import Crop
from app.model.cultivation import create_cultivation
from app.model.field import Field, create_field


def test_create_field(
    field_first_year: db.Field, base_field: db.BaseField, user: db.User, guidelines, fill_db
):
    test_field = create_field(field_first_year.id, guidelines=guidelines)
    assert isinstance(test_field, Field)
    assert test_field.base_id == base_field.id
    assert test_field.year == user.year
    assert test_field.area == field_first_year.area
    assert test_field.field_type == field_first_year.field_type


@pytest.fixture
def test_field(field_second_year, guidelines, fill_db) -> Field:
    field = create_field(field_second_year.id, guidelines=guidelines)
    return field


@pytest.fixture
def test_prev_field(field_first_year, guidelines, fill_db) -> Field:
    field = create_field(field_first_year.id, guidelines=guidelines)
    return field


def test__field_prev_year(test_field: Field, test_prev_field: Field):
    assert test_field.field_prev_year == test_prev_field


def test_previous_crop(test_field: Field):
    (catch_crop, main_crop, second_crop) = test_field.cultivations
    test_field.field_prev_year.cultivations = [main_crop, second_crop]
    assert test_field.previous_crop == test_field.catch_crop
    # remove catch crop from current year
    test_field.cultivations.remove(catch_crop)
    assert test_field.previous_crop == test_field.field_prev_year.second_crop
    # remove second crop from previous year
    test_field.field_prev_year.cultivations.remove(second_crop)
    assert test_field.previous_crop == test_field.field_prev_year.main_crop
    # remove main crop from previous year
    test_field.field_prev_year.cultivations.remove(main_crop)
    assert test_field.previous_crop is None


def test_main_crop(test_field: Field):
    assert test_field.main_crop.cultivation_type is CultivationType.main_crop


def test_second_crop(test_field: Field):
    assert (
        test_field.second_crop.cultivation_type is CultivationType.second_crop
        or test_field.second_crop.cultivation_type is CultivationType.second_main_crop
    )


def test_catch_crop(test_field: Field):
    assert test_field.catch_crop.cultivation_type is CultivationType.catch_crop


def test_total_balance(test_field: Field):
    balance = test_field.total_balance()
    assert balance.n == Decimal(-197)
    assert balance.p2o5 == Decimal("-19.2")
    assert balance.k2o == Decimal("-283.6")
    assert balance.mgo == Decimal(-72)
    assert balance.s == Decimal(-14)
    assert balance.cao == Decimal("-1207.9")
    assert balance.nh4 == Decimal(6)


def test_demands(test_field: Field):
    demands = test_field.demands(test_field.catch_crop)
    assert demands.is_empty
    demands = test_field.demands(test_field.main_crop)
    assert demands.n == -155
    assert demands.p2o5 == -45
    assert demands.k2o == -153
    assert demands.mgo == -39
    assert demands.s == -20
    assert demands.cao == 0
    assert demands.nh4 == 0
    demands = test_field.demands(test_field.second_crop)
    assert demands.n == -100
    assert demands.p2o5 == Decimal("-25.2")
    assert demands.k2o == Decimal("-84.6")
    assert demands.mgo == -9
    assert demands.s == -20
    assert demands.cao == 0
    assert demands.nh4 == 0


def test_reductions(test_field: Field):
    reductions = test_field.reductions(test_field.catch_crop)
    assert reductions.is_empty
    reductions = test_field.reductions(test_field.main_crop)
    assert reductions.n == 25 + 15 + 10
    assert reductions.p2o5 == 57 + 20
    assert reductions.k2o == -72 + 20
    assert reductions.mgo == -50 + 20
    assert reductions.s == 0 + 20
    assert reductions.cao == -1125 - 83 + 1
    assert reductions.nh4 == 0
    reductions = test_field.reductions(test_field.second_crop)
    assert reductions.n == 2
    assert reductions.p2o5 == 0
    assert reductions.k2o == 0
    assert reductions.mgo == 0
    assert reductions.s == 0
    assert reductions.cao == 0
    assert reductions.nh4 == 0


@pytest.mark.parametrize(
    "field_type, expected",
    [
        (FieldType.cropland, False),
        (FieldType.grassland, False),
        (FieldType.exchanged_land, True),
        (FieldType.fallow_cropland, True),
    ],
)
def test_soil_reductions_field_types(test_field: Field, field_type, expected):
    test_field.field_type = field_type
    assert test_field.soil_reductions().is_empty is expected


@pytest.mark.parametrize(
    "option_p205, option_k2o, option_mgo, expected",
    [
        (
            DemandType.demand,
            DemandType.demand,
            DemandType.demand,
            Balance(p2o5=57, k2o=-72, mgo=-50),
        ),
        (
            DemandType.removal,
            DemandType.demand,
            DemandType.demand,
            Balance(p2o5=0, k2o=-72, mgo=-50),
        ),
        (
            DemandType.demand,
            DemandType.removal,
            DemandType.demand,
            Balance(p2o5=57, k2o=0, mgo=-50),
        ),
        (
            DemandType.demand,
            DemandType.demand,
            DemandType.removal,
            Balance(p2o5=57, k2o=-72, mgo=0),
        ),
    ],
)
def test_soil_reductions_demand_options(
    test_field: Field, option_p205, option_k2o, option_mgo, expected
):
    test_field.option_p2o5 = option_p205
    test_field.option_k2o = option_k2o
    test_field.option_mgo = option_mgo
    reductions = test_field.soil_reductions()
    assert reductions.p2o5 == expected.p2o5
    assert reductions.k2o == expected.k2o
    assert reductions.mgo == expected.mgo


def test_soil_reductions_main_crop(test_field: Field):
    reductions = test_field.soil_reductions()
    assert reductions.s == 0
    test_field.cultivations.remove(test_field.main_crop)
    reductions = test_field.soil_reductions()
    assert reductions.s == 0


def test_soil_reductions_liming(test_field: Field):
    test_field.soil_sample.year = test_field.year - 4
    reductions = test_field.soil_reductions()
    assert reductions.cao == -150
    test_field.soil_sample.year = test_field.year - 3
    reductions = test_field.soil_reductions()
    assert reductions.cao == -1125


def test_redelivery(test_field: Field):
    redelivery = test_field.redelivery()
    assert redelivery.n == Decimal(10)
    assert redelivery.p2o5 == Decimal(20)
    assert redelivery.k2o == Decimal(20)
    assert redelivery.mgo == Decimal(20)
    assert redelivery.s == Decimal(20)
    assert redelivery.cao == Decimal(-82)
    assert redelivery.nh4 == Decimal(0)


def test_cao_saldo(test_field: Field):
    assert test_field.field_prev_year.saldo.cao == test_field.cao_saldo()
    test_field.field_prev_year = None
    assert test_field.cao_saldo() == 0


def test_fertilization_redelivery(test_field: Field):
    # only organic fertilization in fall for catch crop
    redelivery = test_field.fertilization_redelivery()
    assert redelivery.n == 10
    assert redelivery.p2o5 == 20
    assert redelivery.k2o == 20
    assert redelivery.mgo == 20
    assert redelivery.s == 20
    assert redelivery.cao == -83
    assert redelivery.nh4 == 0
    # add organic fertilization in previous spring
    spring_fertilization = deepcopy(test_field.fertilizations[0])
    spring_fertilization.cultivation_type = CultivationType.main_crop
    spring_fertilization.measure = MeasureType.org_spring
    test_field.field_prev_year.fertilizations.append(spring_fertilization)
    redelivery = test_field.fertilization_redelivery()
    assert redelivery.n == 20
    # add organic fertilization in current spring
    test_field.fertilizations.append(spring_fertilization)
    redelivery = test_field.fertilization_redelivery()
    assert redelivery.n == 20
    # remove current organic fall fertilization
    test_field.fertilizations[0].amount = 0
    redelivery = test_field.fertilization_redelivery()
    assert redelivery.n == 10
    # remove previous year
    test_field.field_prev_year = None
    redelivery = test_field.fertilization_redelivery()
    assert redelivery.n == 0
    assert redelivery.is_empty


def test_n_total(test_field: Field):
    total = test_field.n_total()
    assert total == 100
    spring_fertilization = deepcopy(test_field.fertilizations[0])
    spring_fertilization.cultivation_type = CultivationType.main_crop
    spring_fertilization.measure = MeasureType.org_spring
    test_field.fertilizations.append(spring_fertilization)
    total = test_field.n_total()
    assert total == 200
    test_field.fertilizations = []
    total = test_field.n_total()
    assert total == 0


@pytest.mark.parametrize(
    "option_p2o5, option_k2o, option_mgo, expected",
    [
        (
            DemandType.demand,
            DemandType.demand,
            DemandType.demand,
            Balance(p2o5=100, k2o=100, mgo=100),
        ),
        (
            DemandType.removal,
            DemandType.demand,
            DemandType.demand,
            Balance(p2o5=0, k2o=100, mgo=100),
        ),
        (
            DemandType.demand,
            DemandType.removal,
            DemandType.demand,
            Balance(p2o5=100, k2o=0, mgo=100),
        ),
        (
            DemandType.demand,
            DemandType.demand,
            DemandType.removal,
            Balance(p2o5=100, k2o=100, mgo=0),
        ),
    ],
)
def test_crop_residues_redelivery(
    test_field: Field,
    cultivation_crop: db.Cultivation,
    barley: db.Crop,
    option_p2o5,
    option_k2o,
    option_mgo,
    expected,
):
    crop = Crop(barley)
    crop_cultivation = create_cultivation(cultivation_crop, crop)
    test_field.field_prev_year.cultivations = [crop_cultivation]
    test_field.field_prev_year.option_p2o5 = option_p2o5
    test_field.field_prev_year.option_k2o = option_k2o
    test_field.field_prev_year.option_mgo = option_mgo
    residues = test_field.crop_residues_redelivery()
    assert residues.n == 0
    assert residues.p2o5 == expected.p2o5
    assert residues.k2o == expected.k2o
    assert residues.mgo == expected.mgo


def test_crop_reductions(test_field: Field):
    test_field.soil_sample.humus = HumusType.less_8
    reductions = test_field.crop_reductions(test_field.main_crop)
    assert reductions.n == 40
    assert reductions.s == 10
    reductions = test_field.crop_reductions(test_field.second_crop)
    assert reductions.n == 2
    assert reductions.s == 10
    reductions = test_field.crop_reductions(test_field.catch_crop)
    assert reductions.n == 0
    assert reductions.s == 0


def test__pre_crop_effect(test_field: Field):
    # test_field.field_type
    reduction = test_field._pre_crop_effect(test_field.main_crop)
    assert reduction == 15
    reduction = test_field._pre_crop_effect(test_field.second_crop)
    assert reduction == 2
    # remove all previous crop possiblilities
    test_field.field_prev_year = None
    test_field.cultivations.remove(test_field.previous_crop)
    reduction = test_field._pre_crop_effect(test_field.main_crop)
    assert reduction == 0


@pytest.mark.parametrize(
    "humus_type, expected",
    [
        (HumusType.less_4, 0),
        (HumusType.less_8, 10),
        (HumusType.less_15, 20),
        (HumusType.less_30, 30),
    ],
)
def test__s_reduction(test_field: Field, humus_type: HumusType, expected):
    test_field.soil_sample.humus = humus_type
    s_reduction = test_field._s_reduction(test_field.main_crop)
    assert s_reduction == expected


def test__s_reduction_no_sample(test_field: Field):
    test_field.soil_sample = None
    s_reduction = test_field._s_reduction(test_field.main_crop)
    assert s_reduction == 0


def test_adjust_nutritional_needs(test_field: Field):
    balance = Balance(n=1, p2o5=1, k2o=1, mgo=1, s=1, cao=1, nh4=1)
    test_field.adjust_nutritional_needs(balance)
    assert balance.n == 0
    assert balance.p2o5 == 0
    assert balance.k2o == 0
    assert balance.mgo == 0
    assert balance.s == 0
    assert balance.cao == 1
    assert balance.nh4 == 1


def test_sum_fertilizations(test_field: Field):
    ferts = test_field.sum_fertilizations()
    assert ferts.n == 6
    assert ferts.p2o5 == 6
    assert ferts.k2o == 6
    assert ferts.mgo == 6
    assert ferts.s == 6
    assert ferts.cao == Decimal("-0.9")
    assert ferts.nh4 == 6
    ferts = test_field.sum_fertilizations(fert_class=FertClass.organic)
    assert ferts.is_empty


def test_sum_modifiers(test_field: Field):
    modifiers = test_field.sum_modifiers()
    assert modifiers.is_empty
    test_field.modifiers.append(Balance(n=10))
    modifiers = test_field.sum_modifiers()
    assert modifiers.n == 10


def test_sum_fall_fertilizations(test_field: Field):
    n_total, nh4 = test_field.sum_fall_fertilizations()
    assert n_total == 100
    assert nh4 == 20
    # remove fall fertilization
    test_field.fertilizations.remove(test_field.fertilizations[0])
    n_total, nh4 = test_field.sum_fall_fertilizations()
    assert n_total == 0
    assert nh4 == 0


def test_create_balances(test_field: Field):
    test_field.create_balances()
    for cultivation in test_field.cultivations:
        assert cultivation.balances is not None
        assert cultivation.balances["cultivation"] is not None
        assert cultivation.balances["organic"] is not None
        assert cultivation.balances["mineral"] is not None


def test_cultivation_balances(test_field: Field):
    test_field.modifiers.append(Balance(title="Test modifier", n=10))
    for cultivation in test_field.cultivations:
        balances, need = test_field.cultivation_balances(cultivation)
        assert balances is not None
        assert isinstance(balances, list)
        titles = [balance.title for balance in balances]
        assert "Crop needs" in titles
        if cultivation.cultivation_type is not CultivationType.catch_crop:
            assert "Nmin" in titles or "Legume delivery" in titles
            assert "Pre-crop effect" in titles
        if cultivation.cultivation_type is CultivationType.second_crop:
            assert "Soil reductions" in titles
        if cultivation.cultivation_type is CultivationType.main_crop:
            assert "Soil reductions" in titles
            assert "Organic redelivery" in titles
            assert "Residue redelivery" in titles
            assert "Lime balance" in titles
            assert "Test modifier" in titles
        assert "Total crop needs" in titles

        assert need is not None
        assert isinstance(need, Balance)
        assert need == balances[-1]


def test_fertilization_balances(test_field: Field):
    for cultivation in test_field.cultivations:
        organic, mineral = test_field.fertilization_balances(cultivation)
        organic_titles = [balance.title for balance in organic]
        mineral_titles = [balance.title for balance in mineral]
        for fertilization in test_field.fertilizations:
            if fertilization.cultivation_type is cultivation.cultivation_type:
                if fertilization.fertilizer.fert_class is FertClass.organic:
                    assert fertilization.fertilizer.name in organic_titles
                if fertilization.fertilizer.fert_class is FertClass.mineral:
                    assert fertilization.fertilizer.name in mineral_titles
