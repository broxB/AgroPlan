from pathlib import Path

from model import Base
from sqlalchemy import create_engine


def _connection(db_path: Path):
    engine = create_engine(f"sqlite:///{db_path}")
    return engine.connect()


def setup_database(db_name: str):
    db_path = Path(__file__).parent / db_name
    Base.metadata.bind = _connection(db_path)
    Base.metadata.create_all()
    print(f"Created database '{db_name}' based on model.")


if __name__ == "__main__":
    setup_database("database_tester.db")
