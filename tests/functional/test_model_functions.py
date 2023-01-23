from time import time

from jwt import encode

from app.database.model import BaseField, Crop, Fertilizer, FertilizerUsage, Field, User
from app.database.types import CropClass, FertClass, FieldType


def test_user_reset_password(user: User, client):
    token = user.get_reset_password_token()
    false_token = encode(
        {"reset_password": user.id, "exp": time()}, "SECRET_KEY", algorithm="HS256"
    )
    verify_token = user.verify_reset_password_token
    assert verify_token(token) == user
    assert verify_token(false_token) is None


def test_user_get_fields(user: User, base_field: BaseField, field: Field, client):
    assert base_field in user.get_fields().all()
    assert base_field in user.get_fields(year=field.year).all()


def test_user_get_years(user: User, field: Field, client):
    assert field.year in user.get_years()


def test_user_get_crops(user: User, crop: Crop, client):
    assert crop in user.get_crops()
    assert crop in user.get_crops(crop_class=crop.crop_class)
    assert crop in user.get_crops(field_type=crop.field_type)


def test_user_get_fertilizers(user: User, fertilizer: Fertilizer, client):
    assert fertilizer in user.get_fertilizers()
    assert fertilizer in user.get_fertilizers(fert_class=fertilizer.fert_class)
    assert fertilizer in user.get_fertilizers(year=fertilizer.year)


def test_user_get_fertilizer_usage(user: User, fertilizer_usage: FertilizerUsage, client):
    assert fertilizer_usage in user.get_fertilizer_usage()
