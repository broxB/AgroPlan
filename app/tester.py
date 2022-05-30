from datetime import datetime
from decimal import Decimal, getcontext
from importlib import resources

from sqlalchemy import and_, asc, create_engine, desc, func
from sqlalchemy.orm import sessionmaker

from database.model import (Crop, CultivatedCrop, Cultivation, Fertilization,
                            Fertilizer, Field)


def main():
    """Main entry point of program"""
    # Connect to the database using SQLAlchemy
    with resources.path("database", "database.db") as sqlite_filepath:
        engine = create_engine(f"sqlite:///{sqlite_filepath}", echo=False, future=True)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    tables = [Field, Cultivation, CultivatedCrop, Crop, Fertilization, Fertilizer]
    # tables = [Cultivation, Fertilization]
    for table in tables:
        print(get_table(session, table))

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
