import sqlite3
from pathlib import Path
from sqlite3 import Error

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    create_engine,
)

DB_FILEPATH = Path(__file__).parent / "database.db"


def create_db(db_path=DB_FILEPATH):
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        print(sqlite3.version)
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()
            print("Created database.db")


def create_table(db_path, drop):
    engine = create_engine(f"sqlite:///{db_path}")
    metadata_obj = MetaData()

    field_cultivation = Table(
        "field_cultivation",
        metadata_obj,
        Column("field_id", Integer, ForeignKey("field.field_id")),
        Column("cultivation_id", Integer, ForeignKey("cultivation.cultivation_id"))
    )

    cultivation_fertilization = Table(
        "cultivation_fertilization",
        metadata_obj,
        Column("cultivation_id", Integer, ForeignKey("cultivation.cultivation_id")),
        Column("fertilization_id", Integer, ForeignKey("fertilization.fertilization_id"))
    )

    field = Table(
        "field",
        metadata_obj,
        Column("field_id", Integer, primary_key=True),
        Column("prefix", Integer),
        Column("suffix", Integer),
        Column("name", String),
        Column("area", Float),
        Column("type", String)
    )

    cultivation = Table(
        "cultivation",
        metadata_obj,
        Column("cultivation_id", Integer, primary_key=True),
        Column("year", Date),
        Column("field_id", Integer, ForeignKey("field.field_id")),
        UniqueConstraint("cultivation_id", "field_id", "year", name="cultivations")
    )

    cultivated_crop = Table(
        "cultivated_crop",
        metadata_obj,
        Column("cultivated_crop_id", Integer, primary_key=True),
        Column(
            "cultivation_id", Integer, ForeignKey("cultivation.cultivation_id")
        ),
        Column("crop_type", String),
        Column("crop_id", Integer, ForeignKey("crop.crop_id")),
        Column("yield", Float),
        Column("remains", Boolean),
        Column("legume_rate", String)
    )

    crop = Table(
        "crop",
        metadata_obj,
        Column("crop_id", Integer, primary_key=True),
        Column("name", String, unique=True)
    )

    fertilization = Table(
        "fertilization",
        metadata_obj,
        Column("fertilization_id", Integer, primary_key=True),
        Column(
            "cultivated_crop_id", Integer, ForeignKey("cultivated_crop.cultivated_crop_id")
        ),
        Column("fertilizer_id", Integer, ForeignKey("fertilizer.fertilizer_id")),
        Column("amount", Float(asdecimal=True)),
        Column("measure", String),
        Column("month", Integer)
    )

    fertilizer = Table(
        "fertilizer",
        metadata_obj,
        Column("fertilizer_id", Integer, primary_key=True),
        Column("name", String, unique=True),
        Column("year", Date),
        Column("type", String),
        Column("active", Boolean, nullable=True)
    )

    if drop: metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)


if __name__ == "__main__":
    # create_db(DB_FILEPATH)
    # create_table(DB_FILEPATH, drop_tables=True)
    pass