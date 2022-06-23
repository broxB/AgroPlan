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
    SoilSample,
    SoilType,
    field_fertilization,
    field_soil_sample,
)
from database.utils import create_session
from sqlalchemy import asc, create_engine, desc, func, or_
from sqlalchemy.orm import Session, sessionmaker


def main():
    # """Main entry point of program"""
    # # Connect to the database using SQLAlchemy
    # with resources.path("database", "database_v3.2.db") as sqlite_filepath:
    #     engine = create_engine(f"sqlite:///{sqlite_filepath}", echo=False, future=True)
    # Session = sessionmaker()
    # Session.configure(bind=engine)
    # session = Session()  # type: Session

    session = create_session(path="app/database/database2.db", use_echo=False)

    # fields = (
    #     session.query(Field.name, Cultivation.crop_class, Crop.name)
    #     .join(Cultivation.field)
    #     .join(Crop)
    #     .filter(
    #         Field.year == 2021,
    #         Field.type == FieldType.cropland,
    #         # Cultivation.crop_class == CropClass.catch_crop,
    #     )
    #     .all()
    # )
    # pprint([(field, cult.value, crop) for (field, cult, crop) in fields])

    usage = (
        session.query(FertilizerUsage)
        .filter(FertilizerUsage.year == 2021, FertilizerUsage.amount < 100)
        .all()
    )
    print(usage, [use.amount for use in usage], sep="\n")

    # pprint(session.query(BaseField).all())
    # pprint(session.query(Field).all())
    # print(session.query(Cultivation).all())
    # print(session.query(Fertilization).all())
    # print(session.query(Crop).all())
    # print(session.query(Fertilizer).all())
    # print(session.query(SoilSample).all())

    # prefix, suffix, name, year = 1, 0, "Am Hof 1", 2022
    # soil_sample = (
    #     session.query(SoilSample)
    #     .join(BaseField)
    #     .filter(
    #         BaseField.prefix == prefix,
    #         BaseField.suffix == suffix,
    #         BaseField.name == name,
    #     )
    #     .all()
    # )
    # pprint(sorted(soil_sample, key=lambda x: x.year, reverse=True))


if __name__ == "__main__":
    main()
