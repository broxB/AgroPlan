from decimal import Decimal

from app.database.model import (
    BaseField,
    Crop,
    Cultivation,
    Fertilization,
    Fertilizer,
    Field,
    Modifier,
    Saldo,
    SoilSample,
    User,
)
from app.database.types import (
    CropClass,
    CropType,
    CultivationType,
    CutTiming,
    DemandType,
    FertClass,
    FertType,
    FieldType,
    HumusType,
    LegumeType,
    MeasureType,
    NminType,
    NutrientType,
    ResidueType,
    SoilType,
    UnitType,
)


def test_user(user: User, base_field: BaseField, fill_db):
    # relationships
    assert base_field in user.fields
    # attributes
    assert user.username == "Test"
    assert user.email == "test@test.test"
    assert user.password_hash != "ValidPassword"
    assert user.year == 1000
    assert user.check_password("ValidPassword")
    assert user.username in str(user.__repr__)


def test_base_field(
    user: User, base_field: BaseField, field_first_year: Field, soil_sample: SoilSample, fill_db
):
    # relationships
    assert base_field.user == user
    assert base_field in user.fields
    assert field_first_year in base_field.fields
    assert soil_sample in base_field.soil_samples
    # attributes
    assert base_field.user_id == user.id
    assert base_field.prefix == 1
    assert base_field.suffix == 0
    assert base_field.name == "Testfield"
    assert base_field.name in str(base_field.__repr__)


def test_field(
    field_first_year: Field,
    base_field: BaseField,
    cultivation_field_grass: Cultivation,
    organic_fertilization: Fertilization,
    fill_db,
):
    # relationships
    assert field_first_year.base_field == base_field
    assert field_first_year in base_field.fields
    assert cultivation_field_grass.field == field_first_year
    assert cultivation_field_grass in field_first_year.cultivations
    assert organic_fertilization.field == field_first_year
    assert organic_fertilization in field_first_year.fertilizations
    # attributes
    assert field_first_year.base_id == base_field.id
    assert field_first_year.sub_suffix == 1
    assert field_first_year.area == Decimal("11.11")
    assert field_first_year.year == 1000
    assert field_first_year.red_region is False
    assert field_first_year.field_type == FieldType.cropland
    assert field_first_year.demand_p2o5 == DemandType.demand
    assert field_first_year.demand_k2o == DemandType.demand
    assert field_first_year.demand_mgo == DemandType.demand
    assert str(field_first_year.area) in str(field_first_year.__repr__)


def test_crop(user: User, main_crop: Crop, cultivation_field_grass: Cultivation, fill_db):
    # relationships
    assert cultivation_field_grass.crop == main_crop
    assert cultivation_field_grass in main_crop.cultivations
    # attributes
    assert main_crop.user_id == user.id
    assert main_crop.name == "Ackergras 3 Schnitte"
    assert main_crop.field_type == FieldType.cropland
    assert main_crop.crop_class == CropClass.main_crop
    assert main_crop.crop_type == CropType.field_grass
    assert main_crop.kind == "Ackergras"
    assert main_crop.feedable is True
    assert main_crop.residue is True
    assert main_crop.nmin_depth == NminType.nmin_0
    assert main_crop.target_demand == 100
    assert main_crop.target_yield == 100
    assert main_crop.pos_yield == 1
    assert main_crop.neg_yield == 2
    assert main_crop.target_protein == Decimal("16")
    assert main_crop.var_protein == Decimal("1.5")
    assert main_crop.p2o5 == Decimal(1)
    assert main_crop.k2o == Decimal(1)
    assert main_crop.mgo == Decimal(1)
    assert main_crop.byproduct == "Heu"
    assert main_crop.byp_ratio == Decimal("0.8")
    assert main_crop.byp_n == Decimal("0.5")
    assert main_crop.byp_p2o5 == Decimal("0.5")
    assert main_crop.byp_k2o == Decimal("0.5")
    assert main_crop.byp_mgo == Decimal("0.5")
    assert main_crop.name in str(main_crop.__repr__)


def test_cultivation(
    field_first_year: Field, main_crop: Crop, cultivation_field_grass: Cultivation, fill_db
):
    # relationships
    assert cultivation_field_grass.field == field_first_year
    assert cultivation_field_grass.crop == main_crop
    # attributes
    assert cultivation_field_grass.field_id == field_first_year.id
    assert cultivation_field_grass.cultivation_type == CultivationType.main_crop
    assert cultivation_field_grass.crop_id == main_crop.id
    assert cultivation_field_grass.crop_yield == 110
    assert cultivation_field_grass.crop_protein == 0
    assert cultivation_field_grass.residues == ResidueType.none
    assert cultivation_field_grass.legume_rate == LegumeType.none
    assert cultivation_field_grass.nmin_30 == 10
    assert cultivation_field_grass.nmin_60 == 10
    assert cultivation_field_grass.nmin_90 == 10
    assert str(cultivation_field_grass.id) in str(cultivation_field_grass.__repr__)


def test_fertilizer(
    user: User, organic_fertilizer: Fertilizer, organic_fertilization: Fertilization, fill_db
):
    # relationships
    assert organic_fertilization.fertilizer == organic_fertilizer
    # attributes
    assert organic_fertilizer.user_id == user.id
    assert organic_fertilizer.name == "Organic Fertilizer"
    assert organic_fertilizer.year == 1000
    assert organic_fertilizer.fert_class == FertClass.organic
    assert organic_fertilizer.fert_type == FertType.org_digestate
    assert organic_fertilizer.active is True
    assert organic_fertilizer.unit == UnitType.cbm
    assert organic_fertilizer.price == Decimal(100)
    assert organic_fertilizer.n == Decimal(1)
    assert organic_fertilizer.p2o5 == Decimal(1)
    assert organic_fertilizer.k2o == Decimal(1)
    assert organic_fertilizer.mgo == Decimal(1)
    assert organic_fertilizer.s == Decimal(1)
    assert organic_fertilizer.cao == Decimal(1)
    assert organic_fertilizer.nh4 == Decimal(1)
    assert organic_fertilizer.name in str(organic_fertilizer.__repr__)


def test_fertilization(
    field_first_year: Field,
    cultivation_field_grass: Cultivation,
    organic_fertilizer: Fertilizer,
    organic_fertilization: Fertilization,
    fill_db,
):
    # relationships
    assert organic_fertilization.cultivation == cultivation_field_grass
    assert organic_fertilization.fertilizer == organic_fertilizer
    assert organic_fertilization.field == field_first_year
    assert organic_fertilization in field_first_year.fertilizations
    # attributes
    assert organic_fertilization.cultivation_id == cultivation_field_grass.id
    assert organic_fertilization.fertilizer_id == organic_fertilizer.id
    assert organic_fertilization.field_id == field_first_year.id
    assert organic_fertilization.cut_timing == CutTiming.none
    assert organic_fertilization.amount == Decimal(10)
    assert organic_fertilization.measure == MeasureType.org_fall
    assert organic_fertilization.month == 10
    assert str(organic_fertilization.amount) in str(organic_fertilization.__repr__)


def test_soil_sample(base_field: BaseField, soil_sample: SoilSample, fill_db):
    # relationships
    assert soil_sample.base_field == base_field
    assert soil_sample in base_field.soil_samples
    # attributes
    assert soil_sample.base_id == base_field.id
    assert soil_sample.year == 1000
    assert soil_sample.ph == Decimal(1)
    assert soil_sample.p2o5 == Decimal(1)
    assert soil_sample.k2o == Decimal(1)
    assert soil_sample.mg == Decimal(1)
    assert soil_sample.soil_type == SoilType.sand
    assert soil_sample.humus == HumusType.less_8
    assert soil_sample.soil_type.value in str(soil_sample.__repr__)


def test_modifier(field_first_year: Field, modifier: Modifier, fill_db):
    # relationships
    assert modifier.field == field_first_year
    assert modifier in field_first_year.modifiers
    # attributes
    assert modifier.description == "Test mod"
    assert modifier.modification is NutrientType.n
    assert modifier.amount == 10


def test_saldo(field_first_year: Field, saldo: Saldo, fill_db):
    # relationships
    assert saldo == field_first_year.saldo
    # attributes
    assert saldo.field_id == field_first_year.id
    assert saldo.n == Decimal(1)
    assert saldo.p2o5 == Decimal(1)
    assert saldo.k2o == Decimal(1)
    assert saldo.mgo == Decimal(1)
    assert saldo.s == Decimal(1)
    assert saldo.cao == Decimal(1)
    assert saldo.n_total == Decimal(1)
