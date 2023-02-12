from dataclasses import dataclass
from decimal import Decimal


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

    def __add__(self, other):
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
