from decimal import Decimal

import pytest

from app.app import create_app
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
from app.extensions import db as _db
from config import TestConfig


@pytest.fixture
def app():
    app = create_app(config_object=TestConfig)
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def db(client):
    _db.create_all()
    yield _db
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user(db) -> User:
    user = User(username="Test", email="test@test.test")
    user.set_password("ValidPassword")
    user.year = 1000
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def base_field(db, user) -> BaseField:
    base_field = BaseField(user_id=user.id, prefix=1, suffix=0, name="Testfield")
    base_field.user = user
    db.session.add(base_field)
    db.session.commit()
    return base_field


@pytest.fixture
def field(db, base_field) -> BaseField:
    field = Field(
        base_id=base_field.id,
        sub_suffix=1,
        area=Decimal("11.11"),
        year=1000,
        red_region=False,
        field_type=FieldType.cropland,
        demand_type=DemandType.demand,
    )
    field.base_field = base_field
    db.session.add(field)
    db.session.commit()
    return field


@pytest.fixture
def crop(db, user) -> Crop:
    crop = Crop(
        user_id=user.id,
        name="Ackergras 3 Schnitte",
        field_type=FieldType.cropland,
        crop_class=CropClass.main_crop,
        crop_type=CropType.field_grass,
        kind="Ackergras",
        feedable=True,
        residue=True,
        legume_rate=LegumeType.main_crop_0,
        nmin_depth=NminType.nmin_0,
        target_demand=Decimal(100),
        target_yield=Decimal(100),
        pos_yield=Decimal(1),
        neg_yield=Decimal(2),
        target_protein=Decimal("16"),
        var_protein=Decimal("1.5"),
        n=Decimal(1),
        p2o5=Decimal(1),
        k2o=Decimal(1),
        mgo=Decimal(1),
        byproduct="Heu",
        byp_ratio=Decimal("0.8"),
        byp_n=Decimal("0.5"),
        byp_p2o5=Decimal("0.5"),
        byp_k2o=Decimal("0.5"),
        byp_mgo=Decimal("0.5"),
    )
    db.session.add(crop)
    db.session.commit()
    return crop


@pytest.fixture
def cultivation(db, crop, field) -> Cultivation:
    cultivation = Cultivation(
        field_id=field.id,
        cultivation_type=CultivationType.main_crop,
        crop_id=crop.id,
        crop_yield=Decimal(110),
        crop_protein=Decimal(),
        residues=ResidueType.main_no_residues,
        legume_rate=LegumeType.none,
        nmin_30=10,
        nmin_60=10,
        nmin_90=10,
    )
    cultivation.crop = crop
    cultivation.field = field
    db.session.add(cultivation)
    db.session.commit()
    return cultivation


@pytest.fixture
def fertilizer(db, user) -> Fertilizer:
    fertilizer = Fertilizer(
        user_id=user.id,
        name="Testfertilizer",
        year=1000,
        fert_class=FertClass.organic,
        fert_type=FertType.org_digestate,
        active=True,
        unit=UnitType.cbm,
        price=Decimal(100),
        n=Decimal(1),
        p2o5=Decimal(1),
        k2o=Decimal(1),
        mgo=Decimal(1),
        s=Decimal(1),
        cao=Decimal(1),
        nh4=Decimal(1),
    )
    db.session.add(fertilizer)
    db.session.commit()
    return fertilizer


@pytest.fixture
def fertilization(db, field, cultivation, fertilizer) -> Fertilization:
    fertilization = Fertilization(
        cultivation_id=cultivation.id,
        fertilizer_id=fertilizer.id,
        cut_timing=CutTiming.non_mowable,
        amount=Decimal(10),
        measure=MeasureType.org_fall,
        month=10,
    )
    fertilization.fertilizer = fertilizer
    fertilization.cultivation = cultivation
    fertilization.field.append(field)
    db.session.add(fertilization)
    db.session.commit()
    return fertilization


@pytest.fixture
def soil_sample(db, base_field, field) -> SoilSample:
    soil_sample = SoilSample(
        base_id=base_field.id,
        year=1000,
        ph=Decimal(1),
        p2o5=Decimal(1),
        k2o=Decimal(1),
        mg=Decimal(1),
        soil_type=SoilType.sand,
        humus=HumusType.less_8,
    )
    soil_sample.fields.append(field)
    db.session.add(soil_sample)
    db.session.commit()
    return soil_sample


@pytest.fixture
def fertilizer_usage(db, user, fertilizer, fertilization, field) -> FertilizerUsage:
    fertilizer_usage = FertilizerUsage(
        user_id=user.id,
        name=fertilizer.name,
        year=field.year,
        amount=field.area * fertilization.amount,
    )
    db.session.add(fertilizer_usage)
    db.session.commit()
    return fertilizer_usage


@pytest.fixture
def saldo(db, field) -> Saldo:
    saldo = Saldo(
        field_id=field.id,
        n=Decimal(1),
        p2o5=Decimal(1),
        k2o=Decimal(1),
        mgo=Decimal(1),
        s=Decimal(1),
        cao=Decimal(1),
        n_total=Decimal(1),
    )
    db.session.add(saldo)
    db.session.commit()
    return saldo
