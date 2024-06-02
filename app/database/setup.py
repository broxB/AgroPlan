from collections import namedtuple

from loguru import logger
from sqlalchemy import select

from app.database.model import (
    Base,
    BaseField,
    Crop,
    Cultivation,
    Fertilization,
    Fertilizer,
    Field,
    Saldo,
    SoilSample,
    User,
)
from app.database.types import (
    CropClass,
    CropType,
    CultivationType,
    CutTiming,
    DemandType,
    FertClass,
    FertType,
    FieldType,
    HumusType,
    LegumeType,
    MeasureType,
    NminType,
    ResidueType,
    SoilType,
    UnitType,
)
from app.extensions import db


def setup_database(seed: list[dict] = None) -> None:
    """Setup or Rebuild database based on model.

    Args:
        db_name (str, optional): File name of the db, NOT the path! Will be created in database directory.
        seed (dict, optional): Sample data to seed into database.
    """
    logger.info("Creating new database.")
    db.drop_all()
    logger.info("Dropping old tables and data.")
    db.create_all()
    logger.info("Creating new tables based on model.")
    if seed is not None:
        seed_database(seed)


def seed_database(data: list[dict]) -> None:
    logger.info("Seeding data into tables.")

    def update_session(data: Base) -> None:
        db.session.add(data)
        db.session.flush()

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
        return DemandType(demand_type)

    def get_crop_type(crop_name: str) -> CropType:
        match crop_name:
            case "Silomais 32%" | "Silomais/Sorghum":
                return CropType.corn
            case "So.-Gerste" | "W.-Gerste" | "W.-Roggen" | "W.-Weizen" | "Hafer" | "GPS-Gerste":
                return CropType.grain
            case "Ackergras 3 Schnitte" | "Ackergras 1 Schnitt" | "Grassamen":
                return CropType.field_grass
            case "Kleegras 1 Schnitt":
                return CropType.clover_grass
            case "Kleegras (30:70)":
                return CropType.clover_grass
            case (
                "Wiese 3 Schnitte"
                | "Weide int. (4-5 Nutz.)"
                | "Mähweide intensiv 20%"
                | "Mähweide intensiv 60%"
                | "Mähweide extensiv 20%"
                | "Mähweide mittel 40%"
                | "Weide extensiv"
                | "Wiese 2 Schnitte"
            ):
                return CropType.permanent_grassland
            case "Nichtleguminosen" | "Senf (GP)":
                return CropType.catch_non_legume
            case "Blühfläche":
                return CropType.rotating_fallow_with_legume
            case "AL-Stilllegung" | "GL-Stilllegung":
                return CropType.rotating_fallow
            case "So.-Raps":
                return CropType.canola
            case _:
                raise ValueError(f"CropType nicht vorhanden für {crop_name=}")

    def get_crop_class(crop_class: str) -> CropClass:
        if crop_class == "Zweitfrucht" or crop_class is None:
            return CropClass.main_crop
        return CropClass(crop_class)

    def get_cultivation_type(cultivation: str) -> CultivationType:
        if cultivation == "Zweitfrucht":
            return CultivationType.second_main_crop
        return CultivationType(cultivation)

    def get_residue_type(remains: str) -> ResidueType:
        try:
            match remains:
                case "verbleiben":
                    return ResidueType.main_stayed
                case _:
                    return ResidueType(remains)
        except ValueError:
            return ResidueType.none

    def get_legume_type(legume: str) -> LegumeType:
        try:
            return LegumeType(legume)
        except ValueError:
            return LegumeType.none

    def get_nmin(nmin_value: int) -> int:
        if nmin_value is not None:
            return nmin_value
        return 0

    def get_fert_class(fert_class: str) -> FertClass:
        match fert_class:
            case "Organisch":
                return FertClass.organic
            case "Mineralisch":
                return FertClass.mineral
            case _:
                raise ValueError(f"FertClass not found. {fert_class=}")

    def get_fert_type(fert_name: str) -> FertType:
        if fert_name.startswith("Gärrest"):
            return FertType.org_digestate
        elif fert_name.startswith("Festmist"):
            return FertType.org_manure
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
        return UnitType(fert_unit)

    def get_soil_type(soil: str) -> SoilType:
        return SoilType(soil)

    def get_humus_type(humus: str) -> HumusType:
        return HumusType(humus)

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
        Fertilizer = namedtuple(
            "Fertilizer", "class_, cut_timing, crop, measure, name, month, amount"
        )
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
                if str(fert).endswith("Schnitt"):
                    fert_timing = CutTiming(fert)
                else:
                    fert_timing = CutTiming.none
                fert_crop = fert_data[i]
                fert_measure = fert_data[i + 1]
                fert_name = fert_data[i + 2]
                fert_amount = str(fert_data[i + offset + 4])
                fert = Fertilizer(
                    fert_class,
                    fert_timing,
                    fert_crop,
                    fert_measure,
                    fert_name,
                    fert_month,
                    fert_amount,
                )
                fertilizations.append(fert)
        return fertilizations

    fields_dict, ferts_dict, crops_dict = data

    user = User(username="Dev-Tester", email="dev@agroplan.de", year=list(fields_dict.keys())[-1])
    user.set_password("test")
    update_session(user)

    for name, fert in ferts_dict.items():
        fertilizer = Fertilizer(
            user_id=user.id,
            name=name,
            year=fert["Jahr"],
            fert_class=get_fert_class(fert["Art"]),
            fert_type=FertType(fert["Gruppe"]),
            active=True,
            unit=get_fert_unit(fert["Einheit"]),
            price=fert["Preis"],
            n=fert["N"],
            p2o5=fert["P2O5"],
            k2o=fert["K2O"],
            mgo=fert["MgO"],
            s=fert["Schwefel"],
            cao=fert["CaO"],
            nh4=fert["NH4"],
        )
        update_session(fertilizer)

    for name, crop_dict in crops_dict.items():
        crop = Crop(
            user_id=user.id,
            name=name,
            field_type=FieldType.cropland,
            crop_class=get_crop_class(crop_dict.get("Klasse", None)),
            crop_type=get_crop_type(name),
            kind=crop_dict.get("Art", None),
            feedable=crop_dict.get("Feldfutter", None),
            residue=crop_dict.get("Erntereste", None),
            nmin_depth=NminType.from_int(crop_dict.get("Nmin_Tiefe", 0)),
            target_demand=crop_dict.get("Richtbedarf", None),
            target_yield=crop_dict.get("Richtertrag", None),
            pos_yield=crop_dict.get("Differenz_Ertrag", [None, None])[1],
            neg_yield=crop_dict.get("Differenz_Ertrag", [None, None])[0],
            target_protein=crop_dict.get("Richt_RP", None),
            var_protein=crop_dict.get("Differenz_RP", None),
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
        update_session(crop)

    for year in fields_dict:
        for field_dict in fields_dict[year]:
            cult_data = field_cultivation(field_dict)
            fert_data = field_fertilization(field_dict)

            base_field = BaseField.query.filter(
                BaseField.prefix == field_dict["Prefix"], BaseField.suffix == field_dict["Suffix"]
            ).one_or_none()
            if base_field is None:
                base_field = BaseField(
                    user_id=user.id,
                    prefix=field_dict["Prefix"],
                    suffix=field_dict["Suffix"],
                    name=field_dict["Name"],
                )
                update_session(base_field)

            field = Field(
                area=field_dict["Ha"],
                year=year,
                red_region=False,
                field_type=get_field_type(field_dict["Nutzungsart"]),
                demand_p2o5=DemandType(field_dict["Düngung_Nach"]),
                demand_k2o=DemandType(field_dict["Düngung_Nach"]),
                demand_mgo=DemandType(field_dict["Düngung_Nach"]),
            )
            field.base_field = base_field
            update_session(field)

            for cult in cult_data:
                crop = Crop.query.filter(Crop.name == cult.name).one_or_none()
                if crop is None:
                    logger.error(f"Crop not found: {cult.name}")
                crop.field_type = field.field_type
                update_session(crop)
                cultivation = Cultivation(
                    field_id=field,
                    cultivation_type=get_cultivation_type(cult.class_),
                    crop_yield=cult.yield_,
                    residues=get_residue_type(cult.remains),
                    legume_rate=get_legume_type(cult.legume),
                    nmin_30=get_nmin(field_dict.get("Nmin30", 0)),
                    nmin_60=get_nmin(field_dict.get("Nmin60", 0)),
                    nmin_90=get_nmin(field_dict.get("Nmin90", 0)),
                )
                cultivation.field = field
                cultivation.crop = crop
                update_session(cultivation)

                for fert in fert_data:
                    if fert.crop != cult.class_ and "Schnitt" not in fert.crop:
                        continue
                    fert_year = year if fert.class_ == FertClass.organic else 0
                    fertilizer = (
                        Fertilizer.query.filter_by(name=fert.name)
                        .filter_by(year=fert_year)
                        .one_or_none()
                    )
                    if fertilizer is None:
                        logger.error(f"Fertilizer not found: {fert.name}")
                    fertilization = Fertilization(
                        cut_timing=CutTiming(fert.cut_timing),
                        measure=MeasureType(fert.measure),
                        amount=fert.amount,
                        month=fert.month,
                    )
                    fertilization.cultivation = cultivation
                    fertilization.fertilizer = fertilizer
                    fertilization.field = field
                    update_session(fertilization)

            saldo = Saldo.query.filter(Saldo.field_id == field.id).one_or_none()
            if saldo is None:
                saldo = Saldo(
                    n=field_dict["N_Saldo"] if field_dict["N_Saldo"] else 0,
                    p2o5=field_dict["P2O5_Saldo"] if field_dict["P2O5_Saldo"] else 0,
                    k2o=field_dict["K2O_Saldo"] if field_dict["K2O_Saldo"] else 0,
                    mgo=field_dict["MgO_Saldo"] if field_dict["MgO_Saldo"] else 0,
                    s=field_dict["S_Saldo"] if field_dict["S_Saldo"] else 0,
                    cao=field_dict["CaO_Saldo"] if field_dict["CaO_Saldo"] else 0,
                    n_total=field_dict["Nges_FD"] if field_dict["Nges_FD"] else 0,
                )
                field.saldo = saldo

            if field_dict["Probedatum"] is None:
                continue
            soil_sample = SoilSample.query.filter(
                SoilSample.base_id == base_field.id,
                SoilSample.ph == field_dict["pH"],
                SoilSample.p2o5 == field_dict["P2O5"],
                SoilSample.k2o == field_dict["K2O"],
                SoilSample.mg == field_dict["Mg"],
            ).one_or_none()
            if soil_sample is None:
                soil_sample = db.session.scalar(
                    select(SoilSample).where(
                        SoilSample.base_id == base_field.id,
                        SoilSample.year == field_dict["Probedatum"],
                    )
                )
                if soil_sample is None:
                    sample_year = field_dict["Probedatum"]
                else:
                    sample_year = field.year
                    logger.info(
                        f"{field.base_field.name}: {field_dict['Probedatum']} -> {field.year}"
                    )
                soil_sample = SoilSample(
                    year=sample_year,
                    ph=field_dict["pH"],
                    p2o5=field_dict["P2O5"],
                    k2o=field_dict["K2O"],
                    mg=field_dict["Mg"],
                    soil_type=get_soil_type(field_dict["Bodenart"]),
                    humus=get_humus_type(field_dict["Humusgehalt"]),
                )
                soil_sample.base_field = base_field
            update_session(soil_sample)

    db.session.commit()
    logger.info("Seeded sample data successfully.")
