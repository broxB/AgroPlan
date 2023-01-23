from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.database.model import BaseField, Field, User


def test_user_reset_password(user: User, client: Flask.test_client, db: SQLAlchemy):
    token = user.get_reset_password_token()
    verified_user = user.verify_reset_password_token(token)
    assert verified_user == user


def test_user_get_fields(
    user: User, base_field: BaseField, client: Flask.test_client, db: SQLAlchemy
):
    assert user.get_fields().all() == [base_field]
