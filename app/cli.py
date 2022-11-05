import contextlib
import os
from pathlib import Path

import click

from app.database.base import Model as Base
from app.database.setup import _seed_database
from app.database.utils import DBConnection
from app.utils import load_json


def register(app):
    # @app.cli.group()
    # def translate():
    #     """Translation and localization commands."""

    # @translate.command()
    # @click.argument("lang")
    # def init(lang):
    #     """Initialize a new language."""
    #     if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
    #         raise RuntimeError("extract command failed")
    #     if os.system("pybabel init -i messages.pot -d app/translations -l " + lang):
    #         raise RuntimeError("init command failed")
    #     os.remove("messages.pot")

    # @translate.command()
    # def update():
    #     """Update all languages."""
    #     if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
    #         raise RuntimeError("extract command failed")
    #     if os.system("pybabel update -i messages.pot -d app/translations"):
    #         raise RuntimeError("update command failed")
    #     os.remove("messages.pot")

    # @translate.command()
    # def compile():
    #     """Compile all languages."""
    #     if os.system("pybabel compile -d app/translations"):
    #         raise RuntimeError("compile command failed")

    @app.cli.group()
    def seed():
        """Seed database"""

    @seed.command()
    def new():
        """Seed database with new data"""
        fields = load_json("data/schläge_reversed.json")
        fertilizers = load_json("data/dünger.json")
        crops = load_json("data/kulturen.json")
        data = [fields, fertilizers, crops]
        db_path = Path(__file__).parent / "database/anbauplanung.db"
        _seed_database(db_path, data)

    @seed.command()
    def reset():
        """Delete all data in existing tables"""
        db_path = Path(__file__).parent / "database/anbauplanung.db"
        engine = DBConnection.connect(url=db_path, echo=False)
        with contextlib.closing(engine.connect()) as con:
            trans = con.begin()
            for table in reversed(Base.metadata.sorted_tables):
                con.execute(table.delete())
            trans.commit()