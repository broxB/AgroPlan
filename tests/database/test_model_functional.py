from time import time

import pytest
from jwt import encode

from app.database.model import (
    BaseField,
    Crop,
    Fertilization,
    Fertilizer,
    Field,
    SoilSample,
    User,
)
from app.database.types import FertClass


def test_user_reset_password(user: User, fill_db):
    token = user.get_reset_password_token()
    false_token = encode(
        {"reset_password": user.id, "exp": time()}, "SECRET_KEY", algorithm="HS256"
    )
    assert user.verify_reset_password_token(token) == user
    assert user.verify_reset_password_token(false_token) is None


def test_user_get_fields(user: User, base_field: BaseField, field_first_year: Field, fill_db):
    assert base_field in user.get_fields().all()
    assert base_field in user.get_fields(year=field_first_year.year).all()


def test_user_get_years(user: User, field_first_year: Field, fill_db):
    assert field_first_year.year in user.get_years()


def test_user_get_crops(user: User, main_crop: Crop, fill_db):
    assert main_crop in user.get_crops()
    assert main_crop in user.get_crops(crop_class=main_crop.crop_class)
    assert main_crop in user.get_crops(field_type=main_crop.field_type)


def test_user_get_fertilizers(
    user: User, organic_fertilizer: Fertilizer, mineral_fertilizer: Fertilizer, fill_db
):
    assert organic_fertilizer in user.get_fertilizers()
    assert organic_fertilizer in user.get_fertilizers(fert_class=organic_fertilizer.fert_class)
    assert organic_fertilizer in user.get_fertilizers(year=organic_fertilizer.year)
    assert organic_fertilizer not in user.get_fertilizers(fert_class=FertClass.mineral)
    assert mineral_fertilizer in user.get_fertilizers(fert_class=FertClass.mineral)
    assert mineral_fertilizer not in user.get_fertilizers(fert_class=FertClass.organic)


def test_field_fertilizers(field_first_year: Field, organic_fertilizer: Fertilizer, fill_db):
    assert organic_fertilizer in field_first_year.fertilizers


def test_field_soil_samples(field_first_year: Field, soil_sample: SoilSample, fill_db):
    assert soil_sample in field_first_year.soil_samples


def test_soilsample_fields(soil_sample: SoilSample, field_first_year: Field, fill_db):
    assert field_first_year in soil_sample.fields


def test_fertilizer_usage(
    organic_fertilizer: Fertilizer,
    mineral_fertilizer: Fertilizer,
    field_first_year: Field,
    organic_fertilization: Fertilization,
    fill_db,
):
    assert (
        organic_fertilizer.usage(field_first_year.year)
        == field_first_year.area * organic_fertilization.amount
    )
    with pytest.raises(ValueError):
        mineral_fertilizer.usage()
