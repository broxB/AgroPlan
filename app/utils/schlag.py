from dataclasses import dataclass


@dataclass
class Schlag:
    Änderungsdatum: str
    Prefix: int
    Suffix: int
    Name: str
    Ha: float
    Nutzungsart: str
    Anbaujahr: int
    Bodenart: str
    pH: float
    P2O5: float
    K2O: float
    Mg: float
    Humusgehalt: str
    Probedatum: int
    Nmin30: int
    Nmin60: int
    Nmin90: int
    Düngung_Nach: str
    Erträge_HF1: int
    Erträge_HF2: int
    Erträge_HF3: int
    Erträge_HF4: int
    Erträge_HF5: int
    Erträge_ZHF1: int
    Erträge_ZHF2: int
    Erträge_ZHF3: int
    Erträge_ZHF4: int
    Erträge_ZHF5: int
    Vorfrucht: str
    Real_Ertrag: float
    Real_Erntereste: str
    Frucht_Kultur1: str
    Frucht_Art1: str
    Frucht_Ertrag1: float
    Frucht_Aussaat1: str
    Frucht_Erntereste1: str
    Frucht_LegAnteil1: str
    Frucht_Kultur2: str
    Frucht_Art2: str
    Frucht_Ertrag2: float
    Frucht_Aussaat2: str
    Frucht_Erntereste2: str
    Frucht_LegAnteil2: str
    Frucht_Kultur3: str
    Frucht_Art3: str
    Frucht_Ertrag3: float
    Frucht_Aussaat3: str
    Frucht_Erntereste3: str
    Frucht_LegAnteil3: str
    OrgDüngung_Kultur1: str
    OrgDüngung_Zeitpunkt1: str
    OrgDüngung_Dünger1: str
    OrgDüngung_Monat1: int
    OrgDüngung_Menge1: int
    OrgDüngung_Kultur2: str
    OrgDüngung_Zeitpunkt2: str
    OrgDüngung_Dünger2: str
    OrgDüngung_Monat2: int
    OrgDüngung_Menge2: int
    OrgDüngung_Kultur3: str
    OrgDüngung_Zeitpunkt3: str
    OrgDüngung_Dünger3: str
    OrgDüngung_Monat3: int
    OrgDüngung_Menge3: int
    OrgDüngung_Kultur4: str
    OrgDüngung_Zeitpunkt4: str
    OrgDüngung_Dünger4: str
    OrgDüngung_Monat4: int
    OrgDüngung_Menge4: int
    OrgDüngung_Kultur5: str
    OrgDüngung_Zeitpunkt5: str
    OrgDüngung_Dünger5: str
    OrgDüngung_Monat5: int
    OrgDüngung_Menge5: int
    MinDüngung_Kultur1: str
    MinDüngung_Maßnahme1: str
    MinDüngung_Dünger1: str
    MinDüngung_Menge1: float
    MinDüngung_Kultur2: str
    MinDüngung_Maßnahme2: str
    MinDüngung_Dünger2: str
    MinDüngung_Menge2: float
    MinDüngung_Kultur3: str
    MinDüngung_Maßnahme3: str
    MinDüngung_Dünger3: str
    MinDüngung_Menge3: float
    MinDüngung_Kultur4: str
    MinDüngung_Maßnahme4: str
    MinDüngung_Dünger4: str
    MinDüngung_Menge4: float
    MinDüngung_Kultur5: str
    MinDüngung_Maßnahme5: str
    MinDüngung_Dünger5: str
    MinDüngung_Menge5: float
    MinDüngung_Kultur6: str
    MinDüngung_Maßnahme6: str
    MinDüngung_Dünger6: str
    MinDüngung_Menge6: float
    MinDüngung_Kultur7: str
    MinDüngung_Maßnahme7: str
    MinDüngung_Dünger7: str
    MinDüngung_Menge7: float
    MinDüngung_Kultur8: str
    MinDüngung_Maßnahme8: str
    MinDüngung_Dünger8: str
    MinDüngung_Menge8: float
    Schn_1: int
    Schn_2: int
    Schn_3: int
    Schn_4: int
    Schn_5: int
    Schn_6: int
    Schn_7: int
    Schn_8: int
    Schn_9: int
    Schn_10: int
    Schn_11: int
    Schn_12: int
    Schn_13: int
    Schn_14: int
    Schn_15: int
    Schn_16: int
    Schn_17: int
    Schn_18: int
    Schn_19: int
    Schn_20: int
    Schn_21: int
    Schn_22: int
    Schn_23: int
    Schn_24: int
    Schn_25: int
    Schn_26: int
    Schn_27: int
    Schn_28: int
    Kalkung: float
    Kalk_Jahre: float
    Kalk_Ha: float
    Nges_HD: float
    Nges_FD: float
    Nges_Saldo: float
    N_Saldo: float
    P2O5_Saldo: float
    K2O_Saldo: float
    MgO_Saldo: float
    S_Saldo: float
    CaO_Saldo: float


if __name__ == "__main__":
    from schlag import Schlag
    from utils import dataclass_from_dict, load_data

    schläge = load_data("data/schläge.json")["2022"]
    for schlag_dict in schläge:
        Feldschlag = dataclass_from_dict(Schlag, schlag_dict)
        print(Feldschlag.Name)