from datetime import date
from decimal import Decimal, getcontext
from importlib import resources

from database.model import (
    Crop,
    Cultivation,
    Fertilization,
    Fertilizer,
    Field,
    SoilSample,
    field_cultivation,
    field_fertilization,
)
from sqlalchemy import asc, create_engine, desc, func, or_
from sqlalchemy.orm import sessionmaker


def main():
    """Main entry point of program"""
    # Connect to the database using SQLAlchemy
    with resources.path("database", "database-v2.0.db") as sqlite_filepath:
        engine = create_engine(f"sqlite:///{sqlite_filepath}", echo=False, future=True)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    # print(session.query(Field).get(1).area)

    print(
        session.query(Field)
        .join(field_cultivation)
        .join(Cultivation)
        .join(Crop)
        .filter(Cultivation.year == 2023, Crop.name == "ZF-Senf")
        .all()
    )
    print(
        session.query(Cultivation)
        .join(Crop)
        .filter(Cultivation.year == 2023, Crop.name == "ZF-Senf")
        .all()
    )

    # print(session.query(Field).all())
    # print(session.query(Cultivation).all())
    # print(session.query(Fertilization).all())
    # print(session.query(Crop).all())
    # print(session.query(Fertilizer).all())
    # print(session.query(SoilSample).all())

    # add_new_field(
    #     session,
    #     prefix=1,
    #     suffix=0,
    #     field_name="Am Hof 1",
    #     area=Decimal(13.89),
    #     type="Grünland",
    # )


def get_table(session, class_):
    """Get a list of author objects sorted by last name"""
    return session.query(class_).all()


# def add_new_field(session, prefix_suffix: str, name: str, area: float, type: str, year: int) -> None:
#     """Adds a new book to the system"""
#     # Get the author's first and last names
#     prefix, suffix = prefix_suffix.split("-")

#     # Check if book exists
#     field = (
#         session.query(Field)
#         .join(Field)
#         .filter(and_(Field.name == name, Field.area = area))
#         .filter(and_(Field.prefix == int(prefix), Field.suffix == int(suffix)))
#         .filter(Field.cultivations.any(Cultivation.year == year))
#         .one_or_none()
#     )
#     # Does the book by the author and publisher already exist?
#     if field is not None:
#         print(f"Field '{name}' already exists!")
#         return

#     # Get the book by the author
#     field = (
#         session.query(Field)
#         .join(Field)
#         .filter(Field.title == area)
#         .filter(and_(Field.name == name, Field.name == name))
#         .one_or_none()
#     )
#     # Create the new book if needed
#     if field is None:
#         field = Field(title=area)

#     # Get the author
#     author = (
#         session.query(Field)
#         .filter(and_(Field.name == name, Field.name == name))
#         .one_or_none()
#     )
#     # Do we need to create the author?
#     if author is None:
#         author = Field(name=name)
#         session.add(author)

#     # Get the publisher
#     publisher = (
#         session.query(Publisher).filter(Publisher.name == type).one_or_none()
#     )
#     # Do we need to create the publisher?
#     if publisher is None:
#         publisher = Publisher(name=type)
#         session.add(publisher)

#     # Initialize the book relationships
#     field.author = author
#     field.publishers.append(publisher)
#     session.add(field)

#     # Commit to the database
#     session.commit()


if __name__ == "__main__":
    main()
