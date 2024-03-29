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


def test_user(user: User):
    assert user.username == "Test"
    assert user.email == "test@test.test"
    assert user.password_hash != "ValidPassword"
    assert user.year == 1000
    assert user.check_password("ValidPassword")
    assert user.username in str(user.__repr__)


def test_base_field(user: User, base_field: BaseField, field: Field, soil_sample: SoilSample):
    # relationships
    assert base_field.user == user
    assert base_field in user.fields
    assert field in base_field.fields
    assert soil_sample in base_field.soil_samples
    # attributes
    assert base_field.user_id == user.id
    assert base_field.prefix == 1
    assert base_field.suffix == 0
    assert base_field.name == "Testfield"
    assert base_field.name in str(base_field.__repr__)


def test_field(
    field: Field,
    base_field: BaseField,
    cultivation: Cultivation,
    fertilization: Fertilization,
):
    # relationships
    assert field.base_field == base_field
    assert field in base_field.fields
    assert cultivation.field == field
    assert cultivation in field.cultivations
    assert fertilization.field == field
    assert fertilization in field.fertilizations
    # attributes
    assert field.base_id == base_field.id
    assert field.sub_suffix == 1
    assert field.area == Decimal("11.11")
    assert field.year == 1000
    assert field.red_region is False
    assert field.field_type == FieldType.cropland
    assert field.demand_p2o5 == DemandType.demand
    assert field.demand_k2o == DemandType.demand
    assert field.demand_mgo == DemandType.demand
    assert str(field.area) in str(field.__repr__)


def test_crop(user: User, crop: Crop, cultivation: Cultivation):
    # relationships
    assert cultivation.crop == crop
    assert cultivation in crop.cultivations
    # attributes
    assert crop.user_id == user.id
    assert crop.name == "Ackergras 3 Schnitte"
    assert crop.field_type == FieldType.cropland
    assert crop.crop_class == CropClass.main_crop
    assert crop.crop_type == CropType.field_grass
    assert crop.kind == "Ackergras"
    assert crop.feedable is True
    assert crop.residue is True
    assert crop.nmin_depth == NminType.nmin_0
    assert crop.target_demand == 100
    assert crop.target_yield == 100
    assert crop.pos_yield == 1
    assert crop.neg_yield == 2
    assert crop.target_protein == Decimal("16")
    assert crop.var_protein == Decimal("1.5")
    assert crop.p2o5 == Decimal(1)
    assert crop.k2o == Decimal(1)
    assert crop.mgo == Decimal(1)
    assert crop.byproduct == "Heu"
    assert crop.byp_ratio == Decimal("0.8")
    assert crop.byp_n == Decimal("0.5")
    assert crop.byp_p2o5 == Decimal("0.5")
    assert crop.byp_k2o == Decimal("0.5")
    assert crop.byp_mgo == Decimal("0.5")
    assert crop.name in str(crop.__repr__)


def test_cultivation(field: Field, crop: Crop, cultivation: Cultivation):
    # relationships
    assert cultivation.field == field
    assert cultivation.crop == crop
    # attributes
    assert cultivation.field_id == field.id
    assert cultivation.cultivation_type == CultivationType.main_crop
    assert cultivation.crop_id == crop.id
    assert cultivation.crop_yield == 110
    assert cultivation.crop_protein == 0
    assert cultivation.residues == ResidueType.none
    assert cultivation.legume_rate == LegumeType.none
    assert cultivation.nmin_30 == 10
    assert cultivation.nmin_60 == 10
    assert cultivation.nmin_90 == 10
    assert str(cultivation.id) in str(cultivation.__repr__)


def test_fertilizer(user: User, fertilizer: Fertilizer):
    # attributes
    assert fertilizer.user_id == user.id
    assert fertilizer.name == "Testfertilizer"
    assert fertilizer.year == 1000
    assert fertilizer.fert_class == FertClass.organic
    assert fertilizer.fert_type == FertType.org_digestate
    assert fertilizer.active is True
    assert fertilizer.unit == UnitType.cbm
    assert fertilizer.price == Decimal(100)
    assert fertilizer.n == Decimal(1)
    assert fertilizer.p2o5 == Decimal(1)
    assert fertilizer.k2o == Decimal(1)
    assert fertilizer.mgo == Decimal(1)
    assert fertilizer.s == Decimal(1)
    assert fertilizer.cao == Decimal(1)
    assert fertilizer.nh4 == Decimal(1)
    assert fertilizer.name in str(fertilizer.__repr__)


def test_fertilization(
    field: Field, cultivation: Cultivation, fertilizer: Fertilizer, fertilization: Fertilization
):
    # relationships
    assert fertilization.cultivation == cultivation
    assert fertilization.fertilizer == fertilizer
    assert fertilization.field == field
    assert fertilization in field.fertilizations
    # attributes
    assert fertilization.cultivation_id == cultivation.id
    assert fertilization.fertilizer_id == fertilizer.id
    assert fertilization.field_id == field.id
    assert fertilization.cut_timing == CutTiming.none
    assert fertilization.amount == Decimal(10)
    assert fertilization.measure == MeasureType.org_fall
    assert fertilization.month == 10
    assert str(fertilization.amount) in str(fertilization.__repr__)


def test_soil_sample(base_field: BaseField, soil_sample: SoilSample):
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


def test_modifier(field: Field, modifier: Modifier):
    # relationships
    assert modifier.field == field
    assert modifier in field.modifiers
    # attributes
    assert modifier.description == "Test mod"
    assert modifier.modification is NutrientType.n
    assert modifier.amount == 10


def test_saldo(field: Field, saldo: Saldo):
    assert saldo.field_id == field.id
    assert saldo.n == Decimal(1)
    assert saldo.p2o5 == Decimal(1)
    assert saldo.k2o == Decimal(1)
    assert saldo.mgo == Decimal(1)
    assert saldo.s == Decimal(1)
    assert saldo.cao == Decimal(1)
    assert saldo.n_total == Decimal(1)
