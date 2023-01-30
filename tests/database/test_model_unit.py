from decimal import Decimal

from app.database.model import (
    BaseField,
    Crop,
    Cultivation,
    Fertilization,
    Fertilizer,
    FertilizerUsage,
    Field,
    Saldo,
    SoilSample,
    User,
    field_fertilization,
    field_soil_sample,
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


def test_base_field(user: User, base_field: BaseField):
    # relationships
    assert base_field in user.fields
    # attributes
    assert base_field.user_id == user.id
    assert base_field.prefix == 1
    assert base_field.suffix == 0
    assert base_field.name == "Testfield"
    assert base_field.name in str(base_field.__repr__)


def test_field(field: Field, base_field: BaseField):
    # relationships
    assert field in base_field.fields
    # attributes
    assert field.base_id == base_field.id
    assert field.sub_suffix == 1
    assert field.area == Decimal("11.11")
    assert field.year == 1000
    assert field.red_region == False
    assert field.field_type == FieldType.cropland
    assert field.demand_type == DemandType.demand
    assert str(field.area) in str(field.__repr__)


def test_crop(user: User, crop: Crop):
    assert crop.user_id == user.id
    assert crop.name == "Ackergras 3 Schnitte"
    assert crop.field_type == FieldType.cropland
    assert crop.crop_class == CropClass.main_crop
    assert crop.crop_type == CropType.field_grass
    assert crop.kind == "Ackergras"
    assert crop.feedable == True
    assert crop.residue == True
    assert crop.legume_rate == LegumeType.main_crop_0
    assert crop.nmin_depth == NminType.nmin_0
    assert crop.target_demand == 100
    assert crop.target_yield == 100
    assert crop.pos_yield == 1
    assert crop.neg_yield == 2
    assert crop.target_protein == Decimal("16")
    assert crop.var_protein == Decimal("1.5")
    assert crop.n == Decimal(1)
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
    # check relationships
    assert cultivation.field == field
    assert cultivation.crop == crop
    # check attributes
    assert cultivation.field_id == field.id
    assert cultivation.cultivation_type == CultivationType.main_crop
    assert cultivation.crop_id == crop.id
    assert cultivation.crop_yield == 110
    assert cultivation.crop_protein == 0
    assert cultivation.residues == ResidueType.main_no_residues
    assert cultivation.legume_rate == LegumeType.none
    assert cultivation.nmin_30 == 10
    assert cultivation.nmin_60 == 10
    assert cultivation.nmin_90 == 10
    assert str(cultivation.id) in str(cultivation.__repr__)


def test_fertilizer(user: User, fertilizer: Fertilizer):
    assert fertilizer.user_id == user.id
    assert fertilizer.name == "Testfertilizer"
    assert fertilizer.year == 1000
    assert fertilizer.fert_class == FertClass.organic
    assert fertilizer.fert_type == FertType.org_digestate
    assert fertilizer.active == True
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
    assert fertilization in field.fertilizations
    # attributes
    assert fertilization.cultivation_id == cultivation.id
    assert fertilization.fertilizer_id == fertilizer.id
    assert fertilization.cut_timing == CutTiming.non_mowable
    assert fertilization.amount == Decimal(10)
    assert fertilization.measure == MeasureType.org_fall
    assert fertilization.month == 10
    assert str(fertilization.amount) in str(fertilization.__repr__)


def test_soil_sample(base_field: BaseField, field: Field, soil_sample: SoilSample):
    # relationships
    assert field in soil_sample.fields
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


def test_fertilizer_usage(
    user: User,
    field: Field,
    fertilizer: Fertilizer,
    fertilization: Fertilization,
    fertilizer_usage: FertilizerUsage,
):
    assert fertilizer_usage.user_id == user.id
    assert fertilizer_usage.name == fertilizer.name
    assert fertilizer_usage.year == field.year
    assert fertilizer_usage.amount == field.area * fertilization.amount
    assert fertilizer_usage.name in str(fertilizer_usage.__repr__)


def test_saldo(field: Field, saldo: Saldo):
    assert saldo.field_id == field.id
    assert saldo.n == Decimal(1)
    assert saldo.p2o5 == Decimal(1)
    assert saldo.k2o == Decimal(1)
    assert saldo.mgo == Decimal(1)
    assert saldo.s == Decimal(1)
    assert saldo.cao == Decimal(1)
    assert saldo.n_total == Decimal(1)


def test_field_fertilization(db, field: Field, fertilization: Fertilization):
    query = (
        db.session.query(field_fertilization)
        .filter_by(field_id=field.id, fertilization_id=fertilization.id)
        .one_or_none()
    )
    assert query is not None


def test_field_soil_sample(db, field: Field, soil_sample: SoilSample):
    query = (
        db.session.query(field_soil_sample)
        .filter_by(field_id=field.id, sample_id=soil_sample.id)
        .one_or_none()
    )
    assert query is not None
