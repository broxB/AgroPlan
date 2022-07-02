import timeit
from decimal import Decimal
from pprint import pprint
from time import time

import model as md
from database.model import (
    BaseField,
    Crop,
    Cultivation,
    Fertilization,
    Fertilizer,
    Field,
    SoilSample,
    field_fertilization,
)
from database.setup import setup_database
from database.types import *
from database.utils import create_session
from utils import load_json


def reseed_database():
    fields = load_json("data/schläge_reversed.json")
    fertilizers = load_json("data/dünger.json")
    crops = load_json("data/kulturen.json")
    data = [fields, fertilizers, crops]
    setup_database("anbauplanung.db", data)
    # seed_extra(fertilizers, crops)


def main():
    start_time = time()
    session = create_session(path="app/database/anbauplanung.db", use_echo=False)

    year = 2022
    db_fields = session.query(Field).filter(Field.year == year).all()

    # db_fields = db_fields[:10]
    total_nges = Decimal()
    for db_field in db_fields:
        field = md.Field(db_field)
        cultivation = md.Cultivation(field)

        for db_cultivation in db_field.cultivations:
            cultivation.cultivations.append(db_cultivation)

        for db_fertilizaiton in db_field.fertilizations:
            fertilizer = md.Fertilizer(db_fertilizaiton.fertilizer)
            fertilization = md.Fertilization(db_fertilizaiton, fertilizer)
            cultivation.fertilizations.append(fertilization)

        measure = None  # MeasureType.spring
        crop_class = None  # CropClass.second_crop
        fert_class = None  # FertClass.organic
        field_nges = cultivation.n_ges(measure=measure, crop_class=crop_class)
        if field_nges > 0:
            print(
                f"{db_field.base_field.name}: ",
                *[
                    f"{fert.fertilization.fertilizer.name}: {[f'{sum:.2f}' for sum in fert.nutrients(cultivation.field.type_)]}"
                    for fert in cultivation.fertilizations
                    if (fert.fertilizer.class_ == fert_class if fert_class else True)
                ],
                f"Nges: "
                f"{[f'{fert.fertilizer.name}: {fert.amount:.1f} {fert.fertilizer.unit.value}' for fert in db_field.fertilizations if fert.fertilizer.fert_class == FertClass.organic and (fert.measure == measure if measure else True)]}"
                f" -> {field_nges:.1f}",
                sep="\n",
                end="\n\n",
            )
        total_nges += field_nges
    print(f"Total: {total_nges:.1f}")
    print(f"Finished in {time() - start_time:.2f} secs")


if __name__ == "__main__":
    main()
    # reseed_database()
