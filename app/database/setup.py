from pathlib import Path

from model import (
    Base,
    Crop,
    CropType,
    Cultivation,
    FertClass,
    Fertilization,
    Fertilizer,
    FertType,
    Field,
    FieldType,
    HumusType,
    MeasureType,
    RemainsType,
    SoilSample,
    SoilType,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _connection(db_path: Path):
    engine = create_engine(f"sqlite:///{db_path}")
    return engine


def setup_database(db_name: str, seed: bool = True) -> None:
    """Setup or Rebuild database based on model.

    Args:
        db_name (str): Name of the db, not the path. Will be created in database directory.
        seed (bool, optional): Seeds sample data into database. Defaults to True.
    """
    db_path = Path(__file__).parent / db_name
    Base.metadata.bind = _connection(db_path).connect()
    operation = "Created"
    if Path(db_path).exists():
        operation = "Accessed"
        Base.metadata.drop_all()
    print(f"{operation} database '{db_name}'.")
    if "Accessed" in operation:
        print("Dropped old tables.")
    Base.metadata.create_all()
    print(f"Created new tables based on model.")
    if seed:
        _seed_database(db_path)


def _add_table_data(db_session: sessionmaker, data: Base) -> None:
    db_session.add(data)
    db_session.flush()


def _seed_database(db_path: str):
    Session = sessionmaker()
    Session.configure(bind=_connection(db_path))
    session = Session()

    field = Field(
        prefix=1,
        suffix=1,
        type=FieldType.cropland,
        name="Am Hof 1",
        area=12.34,
    )
    _add_table_data(session, field)

    crop = Crop(name="W.-Gerste", crop_type="Getreide")
    _add_table_data(session, crop)

    fertilizer = Fertilizer(
        name="Gärrest Herbst 2021",
        year=2022,
        fert_class=FertClass.organic,
        fert_type=FertType.digestate,
    )
    _add_table_data(session, fertilizer)

    cultivation = Cultivation(
        year=2022,
        crop_type=CropType.main_crop,
        crop_yield=50,
        remains=RemainsType.no_remains,
    )
    cultivation.crop = crop
    cultivation.field.append(field)
    _add_table_data(session, cultivation)

    fertilization = Fertilization(amount=10, measure=MeasureType.fall, month=10)
    fertilization.cultivation = cultivation
    fertilization.fertilizer = fertilizer
    fertilization.fields.append(field)
    _add_table_data(session, fertilization)

    soil_sample = SoilSample(
        date=2022,
        ph=5.6,
        p2o5=7,
        k2o=7,
        mg=7,
        soil_type=SoilType.light_loamy_sand,
        humus=HumusType.less_4,
    )
    soil_sample.field = field
    _add_table_data(session, soil_sample)

    session.commit()
    print("Seeded sample data successfully.")


if __name__ == "__main__":
    setup_database("database-v2.0.db")
