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
from app.database.types import DemandType, FieldType
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
    user.year = 2000
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def base_field(db, user) -> BaseField:
    base_field = BaseField(user_id=user, prefix=1, suffix=0, name="Testfield")
    db.session.add(base_field)
    db.session.commit()
    return base_field


@pytest.fixture
def field(db, base_field) -> BaseField:
    field = Field(
        base_id=base_field,
        sub_suffix=1,
        area=Decimal("11.11"),
        year=1,
        red_region=False,
        field_type=FieldType.cropland,
        demand_type=DemandType.demand,
    )
    db.session.add(field)
    db.session.commit()
    return field
