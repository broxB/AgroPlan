from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def create_session(*, path: str = None, use_echo: bool = False) -> Session:
    """Create ``session`` object to make transaction with SQLite database.

    Args:
        path(str, optional): ``File path`` of the db in the current working directory.

    Raises:
        ValueError: Database does not exist.

    Returns:
        Session: Session object which interacts with database.
    """
    if path is None:
        path = "app/database/anbauplanung.db"
    db_path = Path().absolute() / path
    if not db_path.exists():
        raise ValueError(f"Database '{db_path}' does not exist")
    with db_path:
        engine = create_engine(f"sqlite:///{db_path}", echo=use_echo, future=True)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()  # type: Session
    return session
