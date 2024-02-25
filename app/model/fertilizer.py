from __future__ import annotations

from decimal import Decimal

import app.database.model as db
from app.database.types import FertClass, FertType, FieldType

from . import guidelines

from loguru import logger


def create_fertilizer(
    fertilizer: db.Fertilizer, *, guidelines: guidelines = guidelines
) -> Organic | Mineral:
    """
    Facotry to create fertilizers based on their FertClasses.

    :param fertilizer:
        Fertilizer database object
    :return:
        Fertilizer service object.
    """
    if fertilizer.fert_class is FertClass.organic:
        return Organic(fertilizer, guidelines=guidelines)
    elif fertilizer.fert_class is FertClass.mineral:
        return Mineral(fertilizer)


class Fertilizer:
    """
    Class that contains fertilizer specific functions and attributes.
    """

    def __init__(self, Fertilizer: db.Fertilizer):
        self.name: str = Fertilizer.name
        self.fert_class: FertClass = Fertilizer.fert_class
        self.fert_type: FertType = Fertilizer.fert_type
        self.n: Decimal = Fertilizer.n
        self.p2o5: Decimal = Fertilizer.p2o5
        self.k2o: Decimal = Fertilizer.k2o
        self.mgo: Decimal = Fertilizer.mgo
        self.s: Decimal = Fertilizer.s
        self.cao: Decimal = Fertilizer.cao
        self.nh4: Decimal = Fertilizer.nh4

    def is_class(self, fert_class: FertClass) -> bool:
        """
        Check if `Fertilizer` has a certain `FertClass`.

        :param fert_class:
            `FertClass` the fertilizer is compared to.
        """
        return self.fert_class is fert_class if fert_class else True

    @property
    def is_organic(self) -> bool:
        return self.fert_class is FertClass.organic

    @property
    def is_mineral(self) -> bool:
        return self.fert_class is FertClass.mineral

    @property
    def is_lime(self) -> bool:
        return self.fert_type is FertType.lime

    def n_total(self, *arg, **kwargs) -> Decimal:
        """
        Calculates the total nitrogen content.
        """

    def n_verf(self, *arg, **kwargs) -> Decimal:
        """
        Calculates the available nitrogen content.
        """

    def lime_starvation(self, field_type: FieldType) -> Decimal:
        """
        Returns the lime starvation of the fertilizer
        in relation to the field_type it is used on.

        `E = 1 x CaO + 1.4 x MgO + 0.6 x K2O + 0.9 x Na2O - 0.4 x P2O5 - 0.7 x SO3 - 0.8 Cl - n x N`

        Sluijsmans, C.M.J. (1969). Der Einfluss von Düngemitteln auf den Kalkzustand des Bodens.
        Zeitschrift für Pflanzenernährung und Bodenkunde, 126. Band Heft 2 (1970), S. 97-103

        :param field_type:
            `FieldType` of the field it is used on.
        """
        n = {FieldType.cropland: 1, FieldType.grassland: Decimal("0.8")}
        return (
            self.cao
            + Decimal("1.4") * self.mgo
            + Decimal("0.6") * self.k2o
            - Decimal("0.4") * self.p2o5
            - Decimal("0.7") * self.s / Decimal("0.4")  # Conversion from SO3
            - n.get(field_type, 1) * self.n
        )


class Organic(Fertilizer):
    """
    Subclass for organic fertilizers.
    """

    def __init__(self, fertilizer, *, guidelines: guidelines = guidelines):
        super().__init__(fertilizer)
        self._org_factor: dict = guidelines.org_factor()

    def n_total(self, netto: bool = False) -> Decimal:
        """
        Calculates the total nitrogen content.

        :param netto:
            Factor in storage losses.
        """
        return self.n * self._storage_loss() if netto else self.n

    def _storage_loss(self) -> Decimal:
        try:
            return Decimal(str(self._org_factor[self.fert_type.value]["Lagerverluste"]))
        except KeyError as e:
            logger.warning(e)
            return Decimal()

    def n_verf(self, field_type: FieldType) -> Decimal:
        """
        Calculates the available nitrogen content based on `FieldType`.

        :param field_type:
            `FieldType` the fertilizer is used on.
        """
        try:
            return max(self.n * self._factor(field_type), self.nh4)
        except KeyError:
            return Decimal()

    def _factor(self, field_type: FieldType) -> Decimal:
        """
        Return nitrogen multiplicator for given `FieldType`.

        :raises KeyError:
            Raise `KeyError` when there is no multi for a field type, e.g. fallow land.
        """
        try:
            return Decimal(str(self._org_factor[self.fert_type.value][field_type.value]))
        except KeyError:
            raise KeyError

    def lime_starvation(self, field_type: FieldType) -> Decimal:
        """Returns the lime starvation of the fertilizer"""
        if (factor := self._factor(field_type)) >= 0.5:
            n = {FieldType.cropland: 1, FieldType.grassland: Decimal("0.8")}.get(field_type, 1)
        else:
            n = (1 - factor) * 2 + Decimal("0.14") * factor * 2

        return (
            self.cao
            + Decimal("1.4") * self.mgo
            + Decimal("0.6") * self.k2o
            - Decimal("0.4") * self.p2o5
            - Decimal("0.7") * self.s * Decimal("0.400")  # Conversion from SO3
            - n * self.n
        )

    def __repr__(self) -> str:
        return f"<Org fertilizer: {self.name}>"


class Mineral(Fertilizer):
    """
    Subclass for mineral fertilizers.
    """

    def n_total(self, *arg, **kwargs) -> Decimal:
        """
        Calculates the total nitrogen content.
        """
        return self.n

    def n_verf(self, *arg, **kwargs) -> Decimal:
        """
        Calculates the available nitrogen content.
        """
        return max(self.n, self.nh4)

    def __repr__(self) -> str:
        return f"<Min fertilizer: {self.name}>"
