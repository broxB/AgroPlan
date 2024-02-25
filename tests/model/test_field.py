import pytest

import app.database.model as db
from app.model.field import Field, create_field


def test_create_field(
    field_first_year: db.Field, base_field: db.BaseField, user: db.User, fill_db
):
    test_field = create_field(user.id, base_field.id, user.year)
    assert isinstance(test_field, Field)
    assert test_field.base_id == base_field.id
    assert test_field.year == user.year
    assert test_field.area == field_first_year.area
    assert test_field.field_type == field_first_year.field_type
    test_field2 = create_field(user.id, base_field.id, user.year + 1)
    assert test_field2.field_prev_year == test_field


@pytest.fixture
def test_field(base_field, user) -> Field:
    field = create_field(user.id, base_field.id, user.year + 1)
    return field


def test_field_main_crop():
    ...
