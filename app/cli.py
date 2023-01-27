import click

from app.database.setup import setup_database
from app.utils import load_json


def register(app):
    @app.cli.command("seed")
    def seed():
        """Seed database"""
        fields = load_json("data/schläge_reversed.json")
        fertilizers = load_json("data/dünger.json")
        crops = load_json("data/kulturen.json")
        seed = [fields, fertilizers, crops]
        setup_database(seed=seed)
