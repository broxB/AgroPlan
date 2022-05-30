from app.modules.schlag import Schlag
from app.modules.utils import load_data, dataclass_from_dict


def test_schlag() -> None:
    d = load_data("data/schläge.json")["2022"][0]
    S = dataclass_from_dict(Schlag, d)
    assert S.Name == "Am Hof 1"
    assert S.Ha == 30.86
    assert S.Nutzungsart == "GL"
