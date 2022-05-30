import json
from typing import Any, Dict


def dataclass_from_dict(dclass: Any, data_dict: Dict) -> Any:
    """Create dataclass from dictionary.

    Args:
        dclass (dataclass): Dataclass to use for creation.
        data_dict (Dict): Dictionary to feed to dataclass.

    Returns:
        dataclass: Dataclass with dictionary data.
    """
    try:
        fieldtypes = dclass.__annotations__
        return dclass(
            **{f: dataclass_from_dict(fieldtypes[f], data_dict[f]) for f in data_dict}
        )
    except AttributeError:
        if isinstance(data_dict, (tuple, list)):
            return [dataclass_from_dict(dclass.__args__[0], f) for f in data_dict]
        return data_dict


def load_data(filename: str) -> Dict:
    """Load data from ``filename``. Has to be a JSON file.

    Args:
        filename (str): Relative path to json file.

    Returns:
        Dict: Data in dict form.
    """
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def save_data(data: Dict, filename: str) -> None:
    """Save data to ``filename```. Has to be a JSON file.

    Args:
        data (Dict): Dictonary that should be saved.
        filename (str): Relative path to json file.
    """
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def renew_dict(schlag_data: Dict) -> Dict:
    """Add column names to nested dictionary.

    Args:
        schlag_data (Dict): Standard dictionary without column names.

    Returns:
        Dict: Dictionary with column names.
    """
    COL_NAMES = [
        "Änderungsdatum",
        "Prefix",
        "Suffix",
        "Name",
        "Ha",
        "Nutzungsart",
        "Anbaujahr",
        "Bodenart",
        "pH",
        "P2O5",
        "K2O",
        "Mg",
        "Humusgehalt",
        "Probedatum",
        "Nmin30",
        "Nmin60",
        "Nmin90",
        "Düngung_Nach",
        "Erträge_HF1",
        "Erträge_HF2",
        "Erträge_HF3",
        "Erträge_HF4",
        "Erträge_HF5",
        "Erträge_ZHF1",
        "Erträge_ZHF2",
        "Erträge_ZHF3",
        "Erträge_ZHF4",
        "Erträge_ZHF5",
        "Vorfrucht",
        "Real_Ertrag",
        "Real_Erntereste",
        "Frucht_Kultur1",
        "Frucht_Art1",
        "Frucht_Ertrag1",
        "Frucht_Aussaat1",
        "Frucht_Erntereste1",
        "Frucht_LegAnteil1",
        "Frucht_Kultur2",
        "Frucht_Art2",
        "Frucht_Ertrag2",
        "Frucht_Aussaat2",
        "Frucht_Erntereste2",
        "Frucht_LegAnteil2",
        "Frucht_Kultur3",
        "Frucht_Art3",
        "Frucht_Ertrag3",
        "Frucht_Aussaat3",
        "Frucht_Erntereste3",
        "Frucht_LegAnteil3",
        "OrgDüngung_Kultur1",
        "OrgDüngung_Zeitpunkt1",
        "OrgDüngung_Dünger1",
        "OrgDüngung_Monat1",
        "OrgDüngung_Menge1",
        "OrgDüngung_Kultur2",
        "OrgDüngung_Zeitpunkt2",
        "OrgDüngung_Dünger2",
        "OrgDüngung_Monat2",
        "OrgDüngung_Menge2",
        "OrgDüngung_Kultur3",
        "OrgDüngung_Zeitpunkt3",
        "OrgDüngung_Dünger3",
        "OrgDüngung_Monat3",
        "OrgDüngung_Menge3",
        "OrgDüngung_Kultur4",
        "OrgDüngung_Zeitpunkt4",
        "OrgDüngung_Dünger4",
        "OrgDüngung_Monat4",
        "OrgDüngung_Menge4",
        "OrgDüngung_Kultur5",
        "OrgDüngung_Zeitpunkt5",
        "OrgDüngung_Dünger5",
        "OrgDüngung_Monat5",
        "OrgDüngung_Menge5",
        "MinDüngung_Kultur1",
        "MinDüngung_Maßnahme1",
        "MinDüngung_Dünger1",
        "MinDüngung_Menge1",
        "MinDüngung_Kultur2",
        "MinDüngung_Maßnahme2",
        "MinDüngung_Dünger2",
        "MinDüngung_Menge2",
        "MinDüngung_Kultur3",
        "MinDüngung_Maßnahme3",
        "MinDüngung_Dünger3",
        "MinDüngung_Menge3",
        "MinDüngung_Kultur4",
        "MinDüngung_Maßnahme4",
        "MinDüngung_Dünger4",
        "MinDüngung_Menge4",
        "MinDüngung_Kultur5",
        "MinDüngung_Maßnahme5",
        "MinDüngung_Dünger5",
        "MinDüngung_Menge5",
        "MinDüngung_Kultur6",
        "MinDüngung_Maßnahme6",
        "MinDüngung_Dünger6",
        "MinDüngung_Menge6",
        "MinDüngung_Kultur7",
        "MinDüngung_Maßnahme7",
        "MinDüngung_Dünger7",
        "MinDüngung_Menge7",
        "MinDüngung_Kultur8",
        "MinDüngung_Maßnahme8",
        "MinDüngung_Dünger8",
        "MinDüngung_Menge8",
        "Schn_1",
        "Schn_2",
        "Schn_3",
        "Schn_4",
        "Schn_5",
        "Schn_6",
        "Schn_7",
        "Schn_8",
        "Schn_9",
        "Schn_10",
        "Schn_11",
        "Schn_12",
        "Schn_13",
        "Schn_14",
        "Schn_15",
        "Schn_16",
        "Schn_17",
        "Schn_18",
        "Schn_19",
        "Schn_20",
        "Schn_21",
        "Schn_22",
        "Schn_23",
        "Schn_24",
        "Schn_25",
        "Schn_26",
        "Schn_27",
        "Schn_28",
        "Kalkung",
        "Kalk_Jahre",
        "Kalk_Ha",
        "Nges_HD",
        "Nges_FD",
        "Nges_Saldo",
        "N_Saldo",
        "P2O5_Saldo",
        "K2O_Saldo",
        "MgO_Saldo",
        "S_Saldo",
        "CaO_Saldo",
    ]
    schlag_dict = {}
    for key, schläge in schlag_data.items():
        new_schläge = []
        for schlag in schläge:
            new_schläge.append(dict(zip(COL_NAMES, schlag)))
        schlag_dict[key] = new_schläge
    return schlag_dict


if __name__ == "__main__":
    new_dict = renew_dict(load_data("schläge.json"))
    save_data(new_dict, "data/new_schläge2.json")
