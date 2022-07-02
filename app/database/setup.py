from collections import namedtuple
from decimal import Decimal
from pathlib import Path

from database.model import (
    Base,
    BaseField,
    Crop,
    Cultivation,
    Fertilization,
    Fertilizer,
    FertilizerUsage,
    Field,
    SoilSample,
)
from database.types import (
    CropClass,
    CropType,
    DemandType,
    FertClass,
    FertType,
    FieldType,
    HumusType,
    LegumeType,
    MeasureType,
    RemainsType,
    SoilType,
    UnitType,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from utils import load_json


def setup_database(db_name: str, seed: dict) -> None:
    """Setup or Rebuild database based on model.

    Args:
        db_name (str): File name of the db, NOT the path! Will be created in database directory.
        seed (dict, optional): Sample data to seed into database.
    """
    db_path = Path(__file__).parent / db_name
    Base.metadata.bind = _connection(db_path).connect()
    operation = "Created"
    if Path(db_path).exists():
        operation = "Accessed"
        Base.metadata.drop_all()
    print(f"{operation} database '{db_name}'.")
    if "Accessed" in operation:
        print("Dropped old tables.")
    Base.metadata.create_all()
    print(f"Created new tables based on model.")
    if seed:
        _seed_database(db_path, seed)


def _connection(db_path: Path):
    engine = create_engine(f"sqlite:///{db_path}")
    return engine


def _seed_database(db_path: str, data: list[dict]) -> None:
    Session = sessionmaker()
    Session.configure(bind=_connection(db_path))
    session = Session()  # type: Session

    def update_session(db_session: sessionmaker, data: Base) -> None:
        db_session.add(data)
        db_session.flush()

    def get_field_type(short_name: dict[str]) -> FieldType:
        match short_name:
            case "AL":
                return FieldType.cropland
            case "GL":
                return FieldType.grassland
            case "BR":
                return FieldType.fallow_cropland
            case "TF":
                return FieldType.exchanged_land
            case _:
                raise ValueError(f"FieldType nicht vorhanden für {short_name=}")

    def get_demand_type(demand_type: str) -> DemandType:
        try:
            return DemandType(demand_type)
        except ValueError:
            return None

    def get_crop_type(crop_name: str) -> CropType:
        match crop_name:
            case "Silomais 32%":
                return CropType.corn
            case ("So.-Gerste" | "W.-Gerste" | "W.-Roggen" | "W.-Weizen" | "Hafer"):
                return CropType.grain
            case ("Ackergras 3 Schnitte" | "Ackergras 1 Schnitt" | "Grassamen"):
                return CropType.field_grass
            case "Kleegras 1 Schnitt":
                return CropType.clover_grass
            case ("Wiese 3 Schnitte" | "Weide int. (4-5 Nutz.)" | "Mähweide intensiv 20%"):
                return CropType.permanent_grassland
            case ("Nichtleguminosen" | "Senf (GP)"):
                return CropType.non_legume
            case "Blühfläche":
                return CropType.rotating_fallow_with_legume
            case ("AL-Stilllegung" | "GL-Stilllegung"):
                return CropType.rotating_fallow
            case _:
                raise ValueError(f"CropType nicht vorhanden für {crop_name=}")

    def get_crop_class(class_: str) -> CropClass:
        try:
            return CropClass(class_)
        except ValueError:
            return None

    def get_remains_type(remains: str) -> RemainsType:
        try:
            return RemainsType(remains)
        except ValueError:
            return RemainsType(None)

    def get_legume_type(legume: str) -> LegumeType:
        try:
            return LegumeType(legume)
        except ValueError:
            return LegumeType(None)

    def get_fert_type(fert_name: str) -> FertType:
        if fert_name.startswith("Gärrest"):
            return FertType.digestate
        elif fert_name.startswith("Festmist"):
            return FertType.manure
        elif fert_name in ["40-Kali", "Roll-Kali"]:
            return FertType.k
        elif fert_name in [
            "Börde 1",
            "Heerter Hüttenkalk",
            "Konverter Kalk 40+3",
            "Saale 1",
            "Söka 2",
            "Walbecker 85+0",
        ]:
            return FertType.lime
        elif fert_name in ["Harnstoff", "KAS"]:
            return FertType.n
        elif "NP" in fert_name:
            return FertType.n_p
        elif fert_name in ["ssA/Domogran", "YARA Sulfan"]:
            return FertType.n_s
        elif "NPK" in fert_name:
            return FertType.n_p_k_s
        elif fert_name in "Kieserit":
            return FertType.misc
        else:
            raise ValueError(f"FertType nicht vorhanden für {fert_name=}")

    def get_fert_unit(fert_unit: str) -> UnitType:
        try:
            return UnitType(fert_unit)
        except ValueError:
            return None

    def get_soil_type(soil: str) -> SoilType:
        try:
            return SoilType(soil)
        except ValueError:
            return None

    def get_humus_type(humus: str) -> HumusType:
        try:
            return HumusType(humus)
        except ValueError:
            return None

    def field_cultivation(field_data: dict) -> list:
        cult_data = [v for k, v in field_data.items() if k.startswith("Frucht_")]
        cultivations = []
        Cultivation = namedtuple("Cultivation", "class_, name, yield_, remains, legume")
        for i, crop in enumerate(cult_data):
            if crop in ["Hauptfrucht", "Zweitfrucht", "Zwischenfrucht"]:
                cult = Cultivation(str(crop), *[cult_data[i + j] for j in [1, 2, 4, 5]])
                cultivations.append(cult)
        return cultivations

    def field_fertilization(field_data: dict) -> list:
        org_data = [v for k, v in field_data.items() if k.startswith("OrgDüngung_")]
        min_data = [v for k, v in field_data.items() if k.startswith("MinDüngung_")]
        fertilizations = []
        Fertilizer = namedtuple("Fertilizer", "class_, crop, measure, name, month, amount")
        fert_data = org_data + min_data
        for i, fert in enumerate(fert_data):
            if fert in ["Hauptfrucht", "Zweitfrucht", "Zwischenfrucht"] or str(fert).endswith(
                "Schnitt"
            ):
                if i < len(org_data):
                    fert_class = FertClass.organic
                    fert_month = fert_data[i + 3]
                    offset = 0
                else:
                    fert_class = FertClass.mineral
                    fert_month = None
                    offset = -1
                fert_crop = fert_data[i]
                fert_measure = fert_data[i + 1]
                fert_name = fert_data[i + 2]
                fert_amount = str(fert_data[i + offset + 4])
                fert = Fertilizer(
                    fert_class, fert_crop, fert_measure, fert_name, fert_month, fert_amount
                )
                fertilizations.append(fert)
        return fertilizations

    fields_dict, ferts_dict, crops_dict = data

    for year in fields_dict:
        for field_dict in fields_dict[year]:
            cult_data = field_cultivation(field_dict)
            fert_data = field_fertilization(field_dict)

            base_field = (
                session.query(BaseField)
                .filter(
                    BaseField.prefix == field_dict["Prefix"],
                    BaseField.suffix == field_dict["Suffix"],
                )
                .one_or_none()
            )
            if base_field is None:
                base_field = BaseField(
                    prefix=field_dict["Prefix"],
                    suffix=field_dict["Suffix"],
                    name=field_dict["Name"],
                )
                update_session(session, base_field)

            field = Field(
                area=field_dict["Ha"],
                year=year,
                red_region=False,
                field_type=get_field_type(field_dict["Nutzungsart"]),
                demand_type=get_demand_type(field_dict["Düngung_Nach"]),
            )
            field.base_field = base_field
            update_session(session, field)

            for cult in cult_data:
                crop = session.query(Crop).filter(Crop.name == cult.name).one_or_none()
                if crop is None:
                    try:
                        crop_dict = crops_dict[cult.name]
                    except:
                        crop_dict = {}
                    crop = Crop(
                        name=cult.name,
                        crop_class=get_crop_class(crop_dict.get("Klasse", None)),
                        crop_type=get_crop_type(cult.name),
                        kind=crop_dict.get("Art", None),
                        feedable=crop_dict.get("Feldfutter", None),
                        remains=crop_dict.get("Erntereste", None),
                        legume_rate=get_legume_type(crop_dict.get("Leguminosenanteil", None)),
                        nmin_depth=crop_dict.get("Nmin_Tiefe", 0),
                        target_demand=crop_dict.get("Richtbedarf", None),
                        target_yield=crop_dict.get("Richtertrag", None),
                        var_yield=crop_dict.get("Differenz_Ertrag", None),
                        target_protein=crop_dict.get("Richt_RP", None),
                        var_protein=crop_dict.get("Differenz_RP", None),
                        n=crop_dict.get("Nährwerte_Hauptprodukt", [0 for _ in range(4)])[0],
                        p2o5=crop_dict.get("Nährwerte_Hauptprodukt", [0 for _ in range(4)])[1],
                        k2o=crop_dict.get("Nährwerte_Hauptprodukt", [0 for _ in range(4)])[2],
                        mgo=crop_dict.get("Nährwerte_Hauptprodukt", [0 for _ in range(4)])[3],
                        byproduct=crop_dict.get("Nebenprodukt", None),
                        byp_ratio=crop_dict.get("HNV", 0),
                        byp_n=crop_dict.get("Nährwerte_Nebenprodukt", [0 for _ in range(4)])[0],
                        byp_p2o5=crop_dict.get("Nährwerte_Nebenprodukt", [0 for _ in range(4)])[1],
                        byp_k2o=crop_dict.get("Nährwerte_Nebenprodukt", [0 for _ in range(4)])[2],
                        byp_mgo=crop_dict.get("Nährwerte_Nebenprodukt", [0 for _ in range(4)])[3],
                    )
                    update_session(session, crop)
                cultivation = Cultivation(
                    field_id=field,
                    crop_class=CropClass(cult.class_),
                    crop_yield=cult.yield_,
                    remains=get_remains_type(cult.remains),
                    legume_rate=get_legume_type(cult.legume),
                )
                cultivation.field = field
                cultivation.crop = crop
                update_session(session, cultivation)

                for fert in fert_data:
                    if fert.crop != cult.class_ and "Schnitt" not in fert.crop:
                        continue
                    fert_year = year if fert.class_ == FertClass.organic else 0
                    fertilizer = (
                        session.query(Fertilizer)
                        .filter(Fertilizer.name == fert.name)
                        .filter(Fertilizer.year == fert_year)
                        .one_or_none()
                    )
                    if fertilizer is None:
                        fert_dict = ferts_dict[fert.name]
                        fertilizer = Fertilizer(
                            name=fert.name,
                            year=fert_year,
                            fert_class=fert.class_,
                            fert_type=get_fert_type(fert.name),
                            active=True,
                            unit=get_fert_unit(fert_dict["Einheit"]),
                            price=fert_dict["Preis"],
                            n=fert_dict["N"],
                            p2o5=fert_dict["P2O5"],
                            k2o=fert_dict["K2O"],
                            mgo=fert_dict["MgO"],
                            s=fert_dict["Schwefel"],
                            cao=fert_dict["CaO"],
                            nh4=fert_dict["NH4"],
                        )
                    update_session(session, fertilizer)

                    fertilizer_usage = (
                        session.query(FertilizerUsage)
                        .filter(FertilizerUsage.name == fert.name)
                        .filter(FertilizerUsage.year == year)
                        .one_or_none()
                    )
                    if fertilizer_usage is None:
                        fertilizer_usage = FertilizerUsage(
                            name=fert.name,
                            year=year,
                            amount=Decimal(field.area) * Decimal(fert.amount),
                        )
                        fertilizer_usage.fertilizer = fertilizer
                    else:
                        fertilizer_usage.amount += Decimal(field.area) * Decimal(fert.amount)
                    update_session(session, fertilizer_usage)

                    fertilization = Fertilization(
                        measure=MeasureType(fert.measure),
                        amount=fert.amount,
                        month=fert.month,
                    )
                    fertilization.cultivation = cultivation
                    fertilization.fertilizer = fertilizer
                    fertilization.field.append(field)
                    update_session(session, fertilization)

            soil_sample = (
                session.query(SoilSample)
                .filter(
                    SoilSample.base_id == base_field.id,
                    SoilSample.year == field_dict["Probedatum"],
                )
                .one_or_none()
            )
            if soil_sample is None:
                soil_sample = SoilSample(
                    year=field_dict["Probedatum"],
                    ph=field_dict["pH"],
                    p2o5=field_dict["P2O5"],
                    k2o=field_dict["K2O"],
                    mg=field_dict["Mg"],
                    soil_type=get_soil_type(field_dict["Bodenart"]),
                    humus=get_humus_type(field_dict["Humusgehalt"]),
                )
                soil_sample.base_id = base_field.id
            soil_sample.fields.append(field)
            update_session(session, soil_sample)

    session.commit()
    print("Seeded sample data successfully.")


if __name__ == "__main__":
    seed = load_json("data/schläge_reversed.json")
    setup_database("database_v3.1.db", seed)
