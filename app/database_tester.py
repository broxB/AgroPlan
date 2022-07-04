import enum
from datetime import date
from decimal import Decimal, getcontext
from importlib import resources
from pprint import pprint

from database.model import (
    BaseField,
    Crop,
    CropClass,
    Cultivation,
    Fertilization,
    Fertilizer,
    FertilizerUsage,
    Field,
    FieldType,
    HumusType,
    LegumeType,
    RemainsType,
    Saldo,
    SoilSample,
    SoilType,
    field_fertilization,
    field_soil_sample,
)
from database.utils import create_session
from sqlalchemy import asc, create_engine, desc, func, not_, or_
from sqlalchemy.orm import Session, sessionmaker


def main():
    session = create_session(path="app/database/anbauplanung.db", use_echo=False)

    # pprint(session.query(BaseField).all())
    # pprint(session.query(Field).all())
    # pprint(session.query(Cultivation).all())
    # pprint(session.query(Fertilization).all())
    # pprint(session.query(Crop).all())
    # pprint(session.query(Fertilizer).all())
    # pprint(session.query(SoilSample).all())

    # Query fields without a soil sample
    # pprint(session.query(Field).filter(not_(Field.soil_samples.any())).all())

    def inner_join():
        fields = (
            session.query(Field.year, BaseField.name, Crop.name, Cultivation.remains)
            .join(Field, BaseField.id == Field.base_id)
            .join(Cultivation, Field.id == Cultivation.field_id)
            .join(Crop, Crop.id == Cultivation.crop_id)
            .filter(Cultivation.remains == RemainsType.removed)
            .all()
        )
        pprint([(year, field, crop, cult.value) for (year, field, crop, cult) in fields])

    def simple_query():
        usage = (
            session.query(FertilizerUsage)
            .filter(FertilizerUsage.year == 2021, FertilizerUsage.amount < 100)
            .all()
        )
        pprint(usage)

    def complex_query():
        prefix, suffix, name, year = 1, 0, "Am Hof 1", 2022
        soil_sample = (
            session.query(SoilSample)
            .join(BaseField)
            .filter(
                BaseField.prefix == prefix,
                BaseField.suffix == suffix,
                BaseField.name == name,
            )
            .all()
        )
        pprint(sorted(soil_sample, key=lambda x: x.year, reverse=True))

    def relationship_query():
        year = 2022
        db_fields = (
            session.query(Field).filter(Field.fertilizations.any(), Field.year == year).all()
        )
        for db_field in db_fields:
            db_fertilizations = (
                session.query(Fertilization)
                .join(field_fertilization)
                .join(Field)
                .filter(Field.id == db_field.id)
                # .filter(Fertilization.fields.any(Field.id == field.id))
                .all()
            )
            for db_fertilization in db_fertilizations:
                pprint(db_fertilization)

    # inner_join()
    # simple_query()
    # complex_query()
    # relationship_query()


if __name__ == "__main__":
    main()
