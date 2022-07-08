from pathlib import Path

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.future import Engine
from sqlalchemy.orm import Session, sessionmaker


class DBConnection:
    """``Singleton`` class to store/manage database engines."""

    __connections = dict()

    @classmethod
    def connect(cls, url: Path | str, echo: bool) -> Engine:
        """Creates database connection.

        Args:
            url (Path | str): ```Filepath`` to SQLite database.
            echo (bool): Echo SQL expressions issued to the database.

        Returns:
            Engine: Database engine.
        """
        if url not in cls.__connections.keys():
            logger.debug()(f"Establishing connection... {url}")
            cls.__connections[url] = create_engine(url=f"sqlite:///{url}", echo=echo, future=True)
        return cls.__connections[url]


def create_session(
    path: str = None, *, echo: bool = False, autoflush: bool = True, expire_on_commit: bool = True
) -> Session:
    """Create ``Session`` object to make transaction with SQLite database.

    Args:
        path(str, optional): ``File path`` of the db in the current working directory.
        echo(bool, optional): Echo SQL expressions send to the database.
        autoflush(bool, optional): Flush ``Session`` object after commiting.
        expire_on_commit(bool, optional): Call ``Session``.close() after commiting.
    Raises:
        ValueError: Database does not exist.
    Returns:
        Session: Session object which interacts with database.
    """
    if path is None:
        path = Path().absolute() / "app/database/anbauplanung.db"  # ":memory:"
    else:
        path = Path().absolute() / path
        if not path.exists():
            raise ValueError(f"Database '{path}' does not exist")
    engine = DBConnection.connect(url=path, echo=echo)
    Session = sessionmaker(bind=engine, expire_on_commit=expire_on_commit, autoflush=autoflush)
    return Session()
