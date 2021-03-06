from decimal import Decimal
from pprint import pprint
from time import time

import model as md
from model.cultivation import create_cultivation
from database.model import BaseField, Field, Saldo
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


def data_collection(index: int = None, year: int = None, start: int = 0, end: int = -1):
    if index is not None:
        start, end = index, index + 1

    if year is None:
        year = 2022

    session = create_session(path="app/database/anbauplanung.db", echo=False)
    db_fields = session.query(Field).filter(Field.year == year).all() #, Field.cultivations.any()
    db_fields = db_fields[start:end]
    for db_field in db_fields:
        field = md.Field(db_field)

        for db_cultivation in db_field.cultivations:
            crop = md.Crop(db_cultivation.crop, db_cultivation.crop_class)
            cultivation = create_cultivation(db_cultivation, crop)
            field.cultivations.append(cultivation)

        for db_fertilization in db_field.fertilizations:
            fertilizer = md.Fertilizer(db_fertilization.fertilizer)
            crop = md.Crop(
                db_fertilization.cultivation.crop, db_fertilization.cultivation.crop_class
            )
            fertilization = md.Fertilization(db_fertilization, fertilizer, crop, db_fertilization.cultivation.crop_class)
            field.fertilizations.append(fertilization)
        yield field


def visualize_field(field: md.Field, header: bool = True):
    width, precision = 5, 0
    elem = ["N", "P2O5", "K2O", "MgO", "S", "CaO"]

    if header:
        print(f"{field.Field.base_field.prefix}-{field.Field.base_field.suffix} {field.Field.base_field.name} ({field.area:.2f} ha): ")
    for cultivation in field.cultivations:
        if cultivation.crop_class != CropClass.catch_crop:
            if cultivation.crop_class == CropClass.main_crop:
                reductions = field.main_crop_reductions(field.soil_sample)
            elif cultivation.crop_class == CropClass.second_crop:
                print()
                reductions = field.second_crop_reductions()
            print("    ", f"{cultivation.crop_class.value}:  ", [f'{e.center(width)}' for e in elem])
            print("    ", "---------------------------------------------------------------------")
            print("    ", "Demand        ", [f'{demand:{width}.{precision}f}' for demand in cultivation.demand(field.demand_option)])
            print("    ", "Reduction     ", [f'{demand:{width}.{precision}f}' for demand in reductions])
            print("    ", "---------------------------------------------------------------------")
            for fertilization in field.fertilizations:
                if fertilization.crop_class == cultivation.crop_class or fertilization.crop_class == CropClass.catch_crop and cultivation.crop_class == CropClass.main_crop:
                    print("    ", f"{fertilization.fertilizer.name[:14]:14}", [f'{nutrient:{width}.{precision}f}' for nutrient in fertilization.nutrients(field.field_type)])

    field_demand = field.sum_demands()
    field_reduction = field.sum_reductions()
    field_fert = field.sum_fertilizations()
    print("    ", "---------------------------------------------------------------------")
    print("    ", "Saldo         ", [f"{sum(num):{width}.{precision}f}" for num in zip(*[field_demand, field_fert, field_reduction])], end="\n\n")


def log_error(index:int = None, fields: list[md.Field] = None, visual: bool = False, year: int = None, output: bool = True):
    width, precision = 6, 1
    elem = ["N", "P2O5", "K2O", "MgO", "S", "CaO", "Nges"]

    if index is not None:
        start, end = index, index + 1
    else:
        start, end = 0, -1
        index = 0
    if fields is None:
        fields = data_collection(start=start, end=end, year=year)

    def equal(x,y):
        diff = abs(Decimal(x)) - abs(Decimal(y))
        return diff <= Decimal("0.1")

    session = create_session("app/database/anbauplanung.db")
    print("\n","Errors:   ", "Model  vs  DB", end="\n\n")
    for idx, field in enumerate(fields):
        id = idx + index
        field.overfertilization
        saldo = [f"{sum(num):.{precision}f}" for num in zip(*[field.sum_demands(), field.sum_reductions(), field.sum_fertilizations()])]
        saldo += [f"{field.n_total(measure=MeasureType.spring, netto=False):.{precision}f}"]
        db_saldo = session.query(Saldo.n, Saldo.p2o5, Saldo.k2o, Saldo.mgo, Saldo.s, Saldo.cao, Saldo.n_total).filter(Saldo.field_id == field.Field.id).one_or_none()
        if db_saldo:
            db_saldo = [f"{num:.{precision}f}" for num in db_saldo]
            compare = [equal(x,y) for x,y in zip(*[saldo, db_saldo])]
            if not all(compare) and output:
                base_field = field.Field.base_field
                print(f"[{id}]", f"{base_field.prefix}-{base_field.suffix} {base_field.name}", " -> ",
                      f"[{base_field.id}]",
                      f"[{field.year}: {field.Field.id}, {field.field_prev_year.year}: {field.field_prev_year.Field.id}]")
                for i, value in enumerate(compare):
                    if value is False:
                        print("    ", f"{f'{elem[i]}:':>5}", f"{saldo[i]:>{width}}", " != ", f"{db_saldo[i]:{width}}")
                print()
                if visual:
                    visualize_field(header=False, field=field)


if __name__ == "__main__":
    # reseed_database()
    # fields = data_collection(year=2021)
    # for field in fields:
    #     if field.catch_crop:
    #         print(field.Field.base_field.name, [f"{n:.2f}" for n in field.catch_crop.demand(field.demand_option)])
            # visualize_field(field=field)
    log_error(index=None, fields=None, year=2022, output=True, visual=False)
