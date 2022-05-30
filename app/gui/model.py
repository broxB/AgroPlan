from modules.schlag import Schlag
from modules.utils import dataclass_from_dict, load_data


def tester():
    schläge = load_data("data/schläge.json")["2022"]
    for schlag_dict in schläge:
        Feldschlag = dataclass_from_dict(Schlag, schlag_dict)
        print(Feldschlag.Name)
