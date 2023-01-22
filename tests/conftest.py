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
from app.extensions import db as _db
from config import TestConfig


@pytest.fixture
def app():
    app = create_app(config_object=TestConfig)
    with app.app_context():
        yield app


@pytest.fixture
def db(app):
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
