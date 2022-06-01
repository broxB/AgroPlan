import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.database.model import Base, Field


@pytest.fixture(scope="session")
def connection():
    engine = create_engine("sqlite://")
    return engine.connect()


# def seed_database():
#     fields = [
#         {
#             "prefix": 1,
#             "suffix": 0,
#             "name": "Am Hof 1",
#             "area": 12.34,
#             "type": "Grünland",
#         },
#     ]

#     for field in fields:
#         db_field = Field(**field)
#         db_session.add(db_field)
#     db_session.commit()


@pytest.fixture(scope="session")
def setup_database(connection):
    Base.metadata.bind = connection
    Base.metadata.create_all()

    # seed_database()

    yield

    Base.metadata.drop_all()


@pytest.fixture
def db_session(setup_database, connection):
    transaction = connection.begin()
    yield scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=connection)
    )
    transaction.rollback()


def test_field_created(db_session):
    db_session.add(
        Field(prefix=1, suffix=1, name="Am Hof 1", area=12.34, type="Grünland")
    )
    db_session.commit()
    field = db_session.query(Field).all()[0]
    assert field.prefix == 2
    assert field.suffix == 1
    assert field.name == "Am Hof 1"
    assert f"{field.area:.2f}" == "12.34"
    assert field.type == "Grünland"
