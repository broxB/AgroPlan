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
    db_fields = session.query(Field).filter(Field.year == year, Field.cultivations.any()).all()
    # db_fields = session.query(Field).filter(Field.year == year, Field.base_id == 68).all()

    db_fields = db_fields[1:2]
    total_nges = Decimal()
    field_timings = []
    for db_field in db_fields:
        field_time = time()
        field = md.Field(db_field)
        planning = md.Plan(field)
        soil = md.Soil(db_field.soil_samples[0])

        for db_cultivation in db_field.cultivations:
            crop = md.Crop(db_cultivation.crop, db_cultivation.crop_class)
            cultivation = md.Cultivation(db_cultivation, crop)
            planning.cultivations.append(cultivation)

        for db_fertilization in db_field.fertilizations:
            fertilizer = md.Fertilizer(db_fertilization.fertilizer)
            crop = md.Crop(
                db_fertilization.cultivation.crop, db_fertilization.cultivation.crop_class
            )
            fertilization = md.Fertilization(db_fertilization, fertilizer, crop, db_fertilization.cultivation.crop_class)
            planning.fertilizations.append(fertilization)

        measure = None  # MeasureType.spring
        crop_class = None  # CropClass.second_crop
        fert_class = None  # FertClass.organic

        print(f"{db_field.base_field.name}: ")

        # Bedarf und Düngung
        field_demand = planning.sum_demands()
        field_reduction = planning.sum_reductions()
        field_fert = planning.sum_fertilizations(fert_class=fert_class)
        print(
            *[
                f"Demand:",
                [f"{demand:7.2f}" for demand in field_demand],
                f"Reduction:",
                [f"{demand:7.2f}" for demand in field_reduction],
                f"Fertilization:",
                [f"{fert:7.2f}" for fert in field_fert],
                f"Sum:",
                [f"{sum(num):7.2f}" for num in zip(*[field_demand, field_fert, field_reduction])],
            ],
            sep="\n",
        )

        # Liste der Düngungen
        # print(
        #     *[
        #         f"{fert.fertilization.fertilizer.name}: {[f'{sum:.2f}' for sum in fert.nutrients(planning.field_type)]}"
        #         for fert in planning.fertilizations
        #         if (fert.fertilizer.class_ == fert_class if fert_class else True)
        #     ],
        #     sep="\n",
        # )

        # Nges
        field_nges = planning.n_ges(measure=measure, crop_class=crop_class, netto=False)
        total_nges += field_nges
        # print(
        #     f"Nges: "
        #     f"{[f'{fert.fertilizer.name}: {fert.amount:.1f} {fert.fertilizer.unit.value}' for fert in db_field.fertilizations if fert.fertilizer.fert_class == FertClass.organic and (fert.measure == measure if measure else True)]}"
        #     f" -> {field_nges:.1f}",
        # )
        # print(f"NgesHD: {planning.n_ges(measure=MeasureType.fall, netto=True):.2f}", f"NgesFD: {planning.n_ges(measure=MeasureType.spring, netto=False):.2f}", sep="\n")

        field_timings.append((db_field.base_field.name, f"{time() - field_time:.2f}"))
        # print(f"{db_field.base_field.name}: {time() - field_time:.2f}")

        print()

    print(f"Total: {total_nges:.1f}")
    pprint(sorted(field_timings, key=lambda x: x[1], reverse=True)[:5])
    print(f"Finished in {time() - start_time:.2f} secs")


def representation():
    session = create_session(path="app/database/anbauplanung.db", use_echo=False)

    index = 16
    year = 2022
    width, precision = 4, 0

    db_fields = session.query(Field).filter(Field.year == year, Field.cultivations.any()).all()
    db_fields = db_fields[index:]
    for db_field in db_fields:
        field = md.Field(db_field)
        planning = md.Plan(field)
        print(f"{db_field.base_field.prefix}-{db_field.base_field.suffix} {db_field.base_field.name} ({db_field.area:.2f} ha): ")

        for db_cultivation in db_field.cultivations:
            crop = md.Crop(db_cultivation.crop, db_cultivation.crop_class)
            cultivation = md.Cultivation(db_cultivation, crop)
            planning.cultivations.append(cultivation)

        for db_fertilization in db_field.fertilizations:
            fertilizer = md.Fertilizer(db_fertilization.fertilizer)
            crop = md.Crop(
                db_fertilization.cultivation.crop, db_fertilization.cultivation.crop_class
            )
            fertilization = md.Fertilization(db_fertilization, fertilizer, crop, db_fertilization.cultivation.crop_class)
            planning.fertilizations.append(fertilization)

        for cultivation in planning.cultivations:
            if cultivation.crop_class != CropClass.catch_crop:
                if cultivation.crop_class == CropClass.main_crop:
                    reductions = planning.main_crop_reductions(md.Soil(field.soil_sample))
                elif cultivation.crop_class == CropClass.second_crop:
                    reductions = planning.second_crop_reductions()
                print(f"{cultivation.crop_class.value}:")
                print("    ", "Demand        ", [f'{demand:{width}.{precision}f}' for demand in cultivation.demand(field.demand_option)])
                print("    ", "Reduction     ", [f'{demand:{width}.{precision}f}' for demand in reductions])
                print("    ", "---------------------------------------------------------------")
                for fertilization in planning.fertilizations:
                    if fertilization.crop_class == cultivation.crop_class or fertilization.crop_class == CropClass.catch_crop and cultivation.crop_class == CropClass.main_crop:
                        print("    ", f"{fertilization.fertilizer.name[:14]:14}", [f'{nutrient:{width}.{precision}f}' for nutrient in fertilization.nutrients(field.field_type)])

        field_demand = planning.sum_demands()
        field_reduction = planning.sum_reductions()
        field_fert = planning.sum_fertilizations()
        print("    ", "---------------------------------------------------------------")
        print("    ", "Saldo         ", [f"{sum(num):{width}.{precision}f}" for num in zip(*[field_demand, field_fert, field_reduction])], end="\n\n")

if __name__ == "__main__":
    # main()
    # reseed_database()
    representation()
