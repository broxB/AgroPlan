import io
import json
import os

import click

from app.database.setup import setup_database
from app.utils import load_json, save_json
from app.utils.utils import renew_dict


def register(app):
    @app.cli.group()
    def seed():
        """Seed database with sample data."""

    @seed.command()
    @click.argument("path")
    def init(path: str):
        """Make excel json export compatible with database seeding"""
        try:
            new_dict: dict = json.load(io.open(path, "r", encoding="utf-8-sig"))
            reversed_dict = {k: new_dict[k] for k in list(reversed(new_dict.keys()))}
            labeled_dict = renew_dict(reversed_dict)
            save_json(labeled_dict, "data/schläge_reversed.json")
            print("Successfully generated file.")
        except FileNotFoundError:
            print("No valid file provided.")

    @seed.command()
    def apply():
        """Load generated jsons and seed database."""
        fields = load_json("data/schläge_reversed.json")
        fertilizers = load_json("data/dünger.json")
        crops = load_json("data/kulturen.json")
        seed = [fields, fertilizers, crops]
        setup_database(seed=seed)

    @app.cli.command("pytest")
    @click.option("--cov", is_flag=True)
    @click.option("--log", is_flag=True)
    def pytest(cov, log):
        """Start pytest with missing coverage report"""
        if cov:
            os.system("pytest --cov-report term-missing --cov")
        elif log:
            os.system("pytest -o log_cli=true")
        else:
            os.system("pytest")
