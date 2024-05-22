from decimal import Decimal

import pytest

import app.database.model as db
from app.database.types import CultivationType, DemandType, FertClass, FieldType
from app.model.balance import Balance
from app.model.crop import Crop
from app.model.cultivation import create_cultivation
from app.model.field import Field, create_field


def test_create_field(
    field_first_year: db.Field, base_field: db.BaseField, user: db.User, guidelines, fill_db
):
    test_field = create_field(user.id, base_field.id, user.year, guidelines=guidelines)
    assert isinstance(test_field, Field)
    assert test_field.base_id == base_field.id
    assert test_field.year == user.year
    assert test_field.area == field_first_year.area
    assert test_field.field_type == field_first_year.field_type


@pytest.fixture
def test_field(base_field, user, guidelines, fill_db) -> Field:
    field = create_field(user.id, base_field.id, user.year + 1, guidelines=guidelines)
    return field


@pytest.fixture
def test_prev_field(base_field, user, guidelines, fill_db) -> Field:
    field = create_field(user.id, base_field.id, user.year, guidelines=guidelines)
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
    assert balance.n == Decimal(-16)
    assert balance.p2o5 == Decimal("-113.2")
    assert balance.k2o == Decimal("-283.6")
    assert balance.mgo == Decimal(-72)
    assert balance.s == Decimal(6)
    assert balance.cao == Decimal("-1207.9")
    assert balance.nh4 == Decimal(6)


def test_sum_demands(test_field: Field):
    demand = test_field.sum_demands()
    assert demand.n == Decimal(-75)
    assert demand.p2o5 == Decimal("-70.2")
    assert demand.k2o == Decimal("-237.6")
    assert demand.mgo == Decimal(-48)
    assert demand.s == Decimal(-20)
    assert demand.cao == Decimal(0)
    assert demand.nh4 == Decimal(0)
    # make sure catch crop is not calculated
    test_field.cultivations.remove(test_field.catch_crop)
    demand_without_cc = test_field.sum_demands()
    assert demand == demand_without_cc


def test_sum_reductions(test_field: Field):
    reductions = test_field.sum_reductions()
    assert reductions.n == Decimal(53)
    assert reductions.p2o5 == Decimal(-49)
    assert reductions.k2o == Decimal(-52)
    assert reductions.mgo == Decimal(-30)
    assert reductions.s == Decimal(20)
    assert reductions.cao == Decimal(-1207)
    assert reductions.nh4 == Decimal(0)


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
            Balance(p2o5=-69, k2o=-72, mgo=-50),
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
            Balance(p2o5=-69, k2o=0, mgo=-50),
        ),
        (
            DemandType.demand,
            DemandType.demand,
            DemandType.removal,
            Balance(p2o5=-69, k2o=-72, mgo=0),
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
    assert redelivery.n == Decimal(11)
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
    redelivery = test_field.fertilization_redelivery()
    assert redelivery.n == 11
    assert redelivery.p2o5 == 20
    assert redelivery.k2o == 20
    assert redelivery.mgo == 20
    assert redelivery.s == 20
    assert redelivery.cao == -83
    assert redelivery.nh4 == 0
    test_field.fertilizations[0].amount = 0
    redelivery = test_field.fertilization_redelivery()
    assert redelivery.n == 1
    test_field.field_prev_year = None
    redelivery = test_field.fertilization_redelivery()
    assert redelivery.n == 0


def test_n_total(test_field: Field):
    total = test_field.n_total()
    assert total == 100
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
    reductions = test_field.crop_reductions(test_field.main_crop)
    assert reductions.n == 40
    reductions = test_field.crop_reductions(test_field.second_crop)
    assert reductions.n == 2
    reductions = test_field.crop_reductions(test_field.catch_crop)
    assert reductions.n == 0


def test__pre_crop_effect(test_field: Field):
    # test_field.field_type
    reduction = test_field._pre_crop_effect(test_field.main_crop)
    assert reduction == 15
    reduction = test_field._pre_crop_effect(test_field.second_crop)
    assert reduction == 2


@pytest.mark.parametrize(
    "option_p2o5, option_k2o, option_mgo, expected",
    [
        (DemandType.demand, DemandType.demand, DemandType.demand, Balance(p2o5=0, k2o=0, mgo=0)),
        (DemandType.removal, DemandType.demand, DemandType.demand, Balance(p2o5=1, k2o=0, mgo=0)),
        (DemandType.demand, DemandType.removal, DemandType.demand, Balance(p2o5=0, k2o=1, mgo=0)),
        (DemandType.demand, DemandType.demand, DemandType.removal, Balance(p2o5=0, k2o=0, mgo=1)),
    ],
)
def test_adjust_to_demand_option(test_field: Field, option_p2o5, option_k2o, option_mgo, expected):
    test_field.option_p2o5 = option_p2o5
    test_field.option_k2o = option_k2o
    test_field.option_mgo = option_mgo
    # set soil sample classes to E
    test_field.soil_sample.p2o5 = 50
    test_field.soil_sample.k2o = 50
    test_field.soil_sample.mg = 50
    balance = Balance(p2o5=1, k2o=1, mgo=1)
    test_field.adjust_to_demand_option(balance)
    assert balance.p2o5 == expected.p2o5
    assert balance.k2o == expected.k2o
    assert balance.mgo == expected.mgo


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
            assert "Nmin" in titles
            assert "Pre-crop effect" in titles
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
