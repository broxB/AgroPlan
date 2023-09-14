import pytest

from app.database.types import NutrientType
from app.model.balance import Balance, create_modifier


@pytest.fixture
def balance() -> Balance:
    return Balance("test", 1, 2, 3, 4, 5, 6, 7)


def test_unit(balance: Balance):
    assert balance.title == "test"
    assert balance.n == 1
    assert balance.p2o5 == 2
    assert balance.k2o == 3
    assert balance.mgo == 4
    assert balance.s == 5
    assert balance.cao == 6
    assert balance.nh4 == 7


def test_is_empty(balance: Balance):
    assert balance.is_empty is False
    empty_balance = Balance("empty", 0, 0, 0, 0, 0, 0, 0)
    assert empty_balance.is_empty is True


def test_keep_title(balance: Balance):
    # original balance title is kept
    balance += Balance("New Name")
    balance *= Balance("New Name")
    assert balance.title == "test"


def test_add(balance: Balance):
    balance.add(balance)
    assert balance.n == 2
    assert balance.p2o5 == 4
    assert balance.k2o == 6
    assert balance.mgo == 8
    assert balance.s == 10
    assert balance.cao == 12
    assert balance.nh4 == 14
    # only balance instances can used with the add method
    with pytest.raises(AttributeError):
        balance.add(1)


def test_dunder_add_instance(balance: Balance):
    balance += balance
    assert balance.n == 2
    assert balance.p2o5 == 4
    assert balance.k2o == 6
    assert balance.mgo == 8
    assert balance.s == 10
    assert balance.cao == 12
    assert balance.nh4 == 14


def test_dunder_add_constant(balance: Balance):
    balance += 1
    assert balance.n == 2
    assert balance.p2o5 == 3
    assert balance.k2o == 4
    assert balance.mgo == 5
    assert balance.s == 6
    assert balance.cao == 7
    assert balance.nh4 == 8


def test_dunder_sub_instance(balance: Balance):
    balance -= balance
    assert balance.is_empty


def test_dunder_sub_constant(balance: Balance):
    balance -= 1
    assert balance.n == 0
    assert balance.p2o5 == 1
    assert balance.k2o == 2
    assert balance.mgo == 3
    assert balance.s == 4
    assert balance.cao == 5
    assert balance.nh4 == 6


def test_multiplication(balance: Balance):
    balance *= 10
    assert balance.n == 10
    assert balance.p2o5 == 20
    assert balance.k2o == 30
    assert balance.mgo == 40
    assert balance.s == 50
    assert balance.cao == 60
    assert balance.nh4 == 70


@pytest.mark.parametrize(
    "value, amount, expected",
    [
        (NutrientType.n, 10, Balance("modifier", n=10)),
        (NutrientType.p2o5, 10, Balance("modifier", p2o5=10)),
        (NutrientType.k2o, 10, Balance("modifier", k2o=10)),
        (NutrientType.mgo, 10, Balance("modifier", mgo=10)),
        (NutrientType.s, 10, Balance("modifier", s=10)),
        (NutrientType.cao, 10, Balance("modifier", cao=10)),
        (NutrientType.nh4, 10, Balance("modifier", nh4=10)),
    ],
    ids=["n", "p2o5", "k2o", "mgo", "s", "cao", "nh4"],
)
def test_create_modifier(value, amount, expected):
    modifier = create_modifier(name="modifier", value=value, amount=amount)
    assert modifier == expected
