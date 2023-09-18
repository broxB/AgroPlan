import logging
from decimal import Decimal

import pytest

from app.app import create_app
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
from app.extensions import db as _db
from config import TestConfig

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def app():
    logger.info("creating app")
    app = create_app(config_object=TestConfig)
    return app


@pytest.fixture(scope="session")
def client(app):
    logger.info("creating app-context")
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def db(client):
    logger.info("creating db")
    _db.create_all()
    yield _db
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user() -> User:
    user = User(id=1, username="Test", email="test@test.test")
    user.set_password("ValidPassword")
    user.year = 1000
    return user


@pytest.fixture
def base_field(user) -> BaseField:
    base_field = BaseField(id=1, user_id=user.id, prefix=1, suffix=0, name="Testfield")
    base_field.user = user
    return base_field


@pytest.fixture
def field(base_field) -> Field:
    field = Field(
        id=1,
        base_id=base_field.id,
        sub_suffix=1,
        area=Decimal("11.11"),
        year=1000,
        red_region=False,
        field_type=FieldType.cropland,
        demand_type=DemandType.demand,
    )
    field.base_field = base_field
    return field


@pytest.fixture
def crop(user) -> Crop:
    crop = Crop(
        id=1,
        user_id=user.id,
        name="Ackergras 3 Schnitte",
        field_type=FieldType.cropland,
        crop_class=CropClass.main_crop,
        crop_type=CropType.field_grass,
        kind="Ackergras",
        feedable=True,
        residue=True,
        nmin_depth=NminType.nmin_0,
        target_demand=100,
        target_yield=100,
        pos_yield=Decimal(1),
        neg_yield=Decimal(2),
        target_protein=Decimal("16"),
        var_protein=Decimal("1.5"),
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
    return crop


@pytest.fixture
def cultivation(crop, field) -> Cultivation:
    cultivation = Cultivation(
        id=1,
        field_id=field.id,
        cultivation_type=CultivationType.main_crop,
        crop_id=crop.id,
        crop_yield=110,
        crop_protein=Decimal(),
        residues=ResidueType.none,
        legume_rate=LegumeType.none,
        nmin_30=10,
        nmin_60=10,
        nmin_90=10,
    )
    cultivation.crop = crop
    cultivation.field = field
    return cultivation


@pytest.fixture
def fertilizer(user) -> Fertilizer:
    fertilizer = Fertilizer(
        id=1,
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
    return fertilizer


@pytest.fixture
def fertilization(field, cultivation, fertilizer) -> Fertilization:
    fertilization = Fertilization(
        id=1,
        cultivation_id=cultivation.id,
        fertilizer_id=fertilizer.id,
        field_id=field.id,
        cut_timing=CutTiming.none,
        amount=Decimal(10),
        measure=MeasureType.org_fall,
        month=10,
    )
    fertilization.fertilizer = fertilizer
    fertilization.cultivation = cultivation
    fertilization.field = field
    return fertilization


@pytest.fixture
def soil_sample(base_field) -> SoilSample:
    soil_sample = SoilSample(
        id=1,
        base_id=base_field.id,
        year=1000,
        ph=Decimal(1),
        p2o5=Decimal(1),
        k2o=Decimal(1),
        mg=Decimal(1),
        soil_type=SoilType.sand,
        humus=HumusType.less_8,
    )
    soil_sample.base_field = base_field
    return soil_sample


@pytest.fixture
def modifier(field: Field) -> Modifier:
    modifier = Modifier(
        id=1, field_id=field.id, description="Test mod", modification=NutrientType.n, amount=10
    )
    modifier.field = field
    return modifier


@pytest.fixture
def saldo(field) -> Saldo:
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
    return saldo


@pytest.fixture
def fill_db(
    db,
    user,
    base_field,
    field,
    cultivation,
    crop,
    fertilization,
    fertilizer,
    soil_sample,
    saldo,
):
    db.session.add(field)
    db.session.add(fertilization)
    db.session.add(user)
    db.session.add(base_field)
    db.session.add(cultivation)
    db.session.add(crop)
    db.session.add(fertilization)
    db.session.add(fertilizer)
    db.session.add(soil_sample)
    db.session.add(saldo)
    db.session.commit()
