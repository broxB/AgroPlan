from flask import current_app

from app.database.model import User


def test_user(user):
    assert user.username == "Test"
    assert user.email == "test@test.test"
    assert user.password_hash != "ValidPassword"
    assert user.check_password("ValidPassword")
    assert user.year == 2000


def test_user_reset_password(user: User, test_client):
    token = user.get_reset_password_token()
    verified_user = user.verify_reset_password_token(token)
    assert verified_user == user
