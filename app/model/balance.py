from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.database.types import NutrientType


def create_modifier(name: str, value: str | NutrientType, amount: int) -> Balance:
    """Create balance class from modifier values"""

    balance = Balance(title=name)
    if isinstance(value, NutrientType):
        value = value.name
    setattr(balance, value, amount)
    return balance


@dataclass
class Balance:
    """
    Class to handle all nutrients balances.
    Supports addition and subtraction of other `Balance` objects.
    """

    title: str = ""
    n: Decimal = 0
    p2o5: Decimal = 0
    k2o: Decimal = 0
    mgo: Decimal = 0
    s: Decimal = 0
    cao: Decimal = 0
    nh4: Decimal = 0

    @property
    def is_empty(self):
        return self.n + self.p2o5 + self.k2o + self.mgo + self.s + self.cao + self.nh4 == 0

    def __add__(self, other):
        try:
            return Balance(
                self.title,
                self.n + other.n,
                self.p2o5 + other.p2o5,
                self.k2o + other.k2o,
                self.mgo + other.mgo,
                self.s + other.s,
                self.cao + other.cao,
                self.nh4 + other.nh4,
            )
        except AttributeError:
            return Balance(
                self.title,
                self.n + other,
                self.p2o5 + other,
                self.k2o + other,
                self.mgo + other,
                self.s + other,
                self.cao + other,
                self.nh4 + other,
            )

    __radd__ = __add__

    def __sub__(self, other):
        return Balance(
            self.title,
            self.n - other.n,
            self.p2o5 - other.p2o5,
            self.k2o - other.k2o,
            self.mgo - other.mgo,
            self.s - other.s,
            self.cao - other.cao,
            self.nh4 - other.nh4,
        )

    def __mul__(self, other):
        try:
            return Balance(
                self.title,
                self.n * other.n,
                self.p2o5 * other.p2o5,
                self.k2o * other.k2o,
                self.mgo * other.mgo,
                self.s * other.s,
                self.cao * other.cao,
                self.nh4 * other.nh4,
            )
        except AttributeError:
            return Balance(
                self.title,
                self.n * other,
                self.p2o5 * other,
                self.k2o * other,
                self.mgo * other,
                self.s * other,
                self.cao * other,
                self.nh4 * other,
            )
