def test_user(user):
    assert user.username == "Test"
    assert user.email == "test@test.test"
    assert user.password_hash != "ValidPassword"
    assert user.check_password("ValidPassword")
    assert user.year == 2000


def test_base_field(user, base_field):
    assert base_field.user_id == user.id
    assert base_field.prefix == 1
    assert base_field.suffix == 0
    assert base_field.name == "Testfield"


def test_field(field, base_field):
    assert field.base_id == base_field.id
    assert field.sub_suffix == 1
    assert str(field.area) == "11.11"
    assert field.year == 1000
    assert field.red_region == False
    assert field.field_type.name == "cropland"
    assert field.demand_type.name == "demand"
