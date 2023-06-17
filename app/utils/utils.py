import json
import re
from decimal import InvalidOperation
from numbers import Number

from loguru import logger


def handle_error(caller, on_exception="None"):
    try:
        return caller()
    except Exception as e:
        logger.error(f"Jinja2 Template erroring with: {e}")
        return on_exception


def format_number(input: Number, format: str = ".2f", ending: str = "") -> str:
    try:
        decimal = int(re.findall(f"\.(\d+)\w", format)[0])
    except IndexError:
        logger.warning("Invalid format used!")
        decimal = 2
    try:
        num = round_to_nearest(input, decimal)
        return f"{num:{format}} {ending}"
    except InvalidOperation:
        return "E"
    except Exception as e:
        logger.warning(f"Error in rounding: {e}")
        return f"N/A {ending}"


def round_to_nearest(number: Number, num_decimals: int) -> Number:
    """python uses banking round; while this round 0.5 up"""
    if (number * 10 ** (num_decimals + 1)) % 10 == 5:
        return round(((number * 10 + 1) / 10) ** (num_decimals + 1), num_decimals)
    else:
        return round(number, num_decimals)


def load_json(filename: str) -> dict:
    """Load data from ``filename``. Has to be a JSON file.

    Args:
        filename (str): Relative path to json file.

    Returns:
        dict: Data in dict form.
    """
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def save_json(data: dict, filename: str) -> None:
    """Save data to ``filename```. Has to be a JSON file.

    Args:
        data (dict): Dictonary that should be saved.
        filename (str): Relative path to json file.
    """
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def renew_dict(schlag_data: dict) -> dict:
    """Add column names to nested dictionary.

    Args:
        schlag_data (dict): Standard dictionary without column names.

    Returns:
        dict: Dictionary with column names.
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
