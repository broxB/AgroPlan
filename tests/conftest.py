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


@pytest.fixture
def test_client():
    app = create_app()
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def user() -> User:
    user = User(username="Test", email="test@test.test")
    user.set_password("ValidPassword")
    user.year = 2000
    return user
