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


def test_addition(balance: Balance):
    balance_added = balance + balance
    balance += balance
    # inplace method is equal to standard method
    assert balance_added == balance
    assert balance.title == "test"
    assert balance.n == 2
    assert balance.p2o5 == 4
    assert balance.k2o == 6
    assert balance.mgo == 8
    assert balance.s == 10
    assert balance.cao == 12
    assert balance.nh4 == 14
    # original balance title is kept
    balance += Balance("New Name")
    assert balance.title == "test"


def test_add_constant(balance: Balance):
    """Add a constant instead of another instance"""
    balance += 1
    assert balance.n == 2
    assert balance.p2o5 == 3
    assert balance.k2o == 4
    assert balance.mgo == 5
    assert balance.s == 6
    assert balance.cao == 7
    assert balance.nh4 == 8


def test_multiplication(balance: Balance):
    balance_multiplied = balance * 10
    balance *= 10
    # inplace method is equal to standard method
    assert balance_multiplied == balance
    assert balance.title == "test"
    assert balance.n == 10
    assert balance.p2o5 == 20
    assert balance.k2o == 30
    assert balance.mgo == 40
    assert balance.s == 50
    assert balance.cao == 60
    assert balance.nh4 == 70
    # original balance title is kept
    balance *= Balance("New Name")
    assert balance.title == "test"


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
