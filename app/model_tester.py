from decimal import Decimal
from pprint import pprint
from time import time

import model as md
from database.model import (
    BaseField,
    Field,
    Saldo,
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


def data_collection(index: int = None, year: int = None, start: int = 0, end: int = -1):
    if index is not None:
        start, end = index, index + 1

    if year is None:
        year = 2022

    session = create_session(path="app/database/anbauplanung.db", use_echo=False)
    db_fields = session.query(Field).filter(Field.year == year, Field.cultivations.any()).all()
    db_fields = db_fields[start:end]
    for db_field in db_fields:
        field = md.Field(db_field)
        planning = md.Plan(field)

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
        yield planning


def visualize_plan(plan: md.Plan, header: bool = True):
    width, precision = 5, 0
    elem = ["N", "P2O5", "K2O", "MgO", "S", "CaO"]

    field = plan.field
    if header:
        print(f"{field.Field.base_field.prefix}-{field.Field.base_field.suffix} {field.Field.base_field.name} ({field.Field.area:.2f} ha): ")
    for cultivation in plan.cultivations:
        if cultivation.crop_class != CropClass.catch_crop:
            if cultivation.crop_class == CropClass.main_crop:
                reductions = plan.main_crop_reductions(field.soil_sample)
            elif cultivation.crop_class == CropClass.second_crop:
                reductions = plan.second_crop_reductions()
            print("    ", f"{cultivation.crop_class.value}:  ", [f'{e.center(width)}' for e in elem])
            print("    ", "---------------------------------------------------------------------")
            print("    ", "Demand        ", [f'{demand:{width}.{precision}f}' for demand in cultivation.demand(field.demand_option)])
            print("    ", "Reduction     ", [f'{demand:{width}.{precision}f}' for demand in reductions])
            print("    ", "---------------------------------------------------------------------")
            for fertilization in plan.fertilizations:
                if fertilization.crop_class == cultivation.crop_class or fertilization.crop_class == CropClass.catch_crop and cultivation.crop_class == CropClass.main_crop:
                    print("    ", f"{fertilization.fertilizer.name[:14]:14}", [f'{nutrient:{width}.{precision}f}' for nutrient in fertilization.nutrients(field.field_type)])

    field_demand = plan.sum_demands()
    field_reduction = plan.sum_reductions()
    field_fert = plan.sum_fertilizations()
    print("    ", "---------------------------------------------------------------------")
    print("    ", "Saldo         ", [f"{sum(num):{width}.{precision}f}" for num in zip(*[field_demand, field_fert, field_reduction])], end="\n\n")


def log_error(index:int = None, plans: list[md.Plan] = None, visual: bool = False):
    width, precision = 6, 1
    elem = ["N", "P2O5", "K2O", "MgO", "S", "CaO"]

    if index is not None:
        start, end = index, index + 1
    else:
        start, end = 0, -1
        index = 0
    if plans is None:
        plans = data_collection(start=start, end=end)

    def equal(x,y):
        diff = abs(Decimal(x)) - abs(Decimal(y))
        return diff <= Decimal("0.1")

    session = create_session()
    print("\n","Errors:   ", "Model  vs  DB", end="\n\n")
    for idx, plan in enumerate(plans):
        id = idx + index
        saldo = [f"{sum(num):.{precision}f}" for num in zip(*[plan.sum_demands(), plan.sum_reductions(), plan.sum_fertilizations()])]
        db_saldo = session.query(Saldo.n, Saldo.p2o5, Saldo.k2o, Saldo.mgo, Saldo.s, Saldo.cao).filter(Saldo.field_id == plan.field.Field.id).one_or_none()
        if db_saldo:
            db_saldo = [f"{num:.{precision}f}" for num in db_saldo]
            compare = [equal(x,y) for x,y in zip(*[saldo, db_saldo])]
            if not all(compare):
                base_field = plan.field.Field.base_field
                print(f"[{id}]", f"{base_field.prefix}-{base_field.suffix} {base_field.name}", " -> ",
                      f"[{base_field.id}]",
                      f"[{plan.year}: {plan.field.Field.id}, {plan.plan_prev_year.year}: {plan.plan_prev_year.field.Field.id}]")
                for i, value in enumerate(compare):
                    if value is False:
                        print("    ", f"{f'{elem[i]}:':>5}", f"{saldo[i]:>{width}}", " != ", f"{db_saldo[i]:{width}}")
                print()
                if visual:
                    visualize_plan(id, header=False, plan=plan)


def timing(header: int = -1, reverse: bool = True):
    # session = create_session(path="app/database/anbauplanung.db", use_echo=False)
    # db_fields = session.query(Field).filter(Field.year == 2022, Field.cultivations.any()).all()
    # plans = []
    # for db_field in db_fields:
    #     field = md.Field(db_field)
    #     planning = md.Plan(field)

    #     for db_cultivation in db_field.cultivations:
    #         crop = md.Crop(db_cultivation.crop, db_cultivation.crop_class)
    #         cultivation = md.Cultivation(db_cultivation, crop)
    #         planning.cultivations.append(cultivation)

    #     for db_fertilization in db_field.fertilizations:
    #         fertilizer = md.Fertilizer(db_fertilization.fertilizer)
    #         crop = md.Crop(
    #             db_fertilization.cultivation.crop, db_fertilization.cultivation.crop_class
    #         )
    #         fertilization = md.Fertilization(db_fertilization, fertilizer, crop, db_fertilization.cultivation.crop_class)
    #         planning.fertilizations.append(fertilization)
    #     plans.append(planning)
    plans: list[md.Plan] = data_collection(year=2022)
    print(f"Start timing:")
    start_time = time()
    field_timings = []
    for plan in plans:
        field_name = plan.field.Field.base_field.name
        field_time = time()

        field_demand = plan.sum_demands()
        time_demand = time() - field_time

        field_reduction = plan.sum_reductions()
        time_reduction = time() - field_time - time_demand

        field_fert = plan.sum_fertilizations()
        time_fert = time() - field_time - time_reduction

        times = [time_demand, time_reduction, time_fert]
        field_timing = time() - field_time
        field_sum = [field_demand, field_reduction, field_fert]
        field_timings.append((field_name, f"{field_timing:.2f}", [f"{time:.2f}" for time in times]))

    finish_time = time() - start_time
    pprint(sorted(field_timings, key=lambda x: x[1], reverse=reverse)[:header])
    print(f"Finished in {finish_time:.2f} secs")


def small_timing(index: int = None, name: str = True):
    session = create_session(path="app/database/anbauplanung.db", use_echo=False)
    db_field = session.query(Field).join(BaseField).filter(Field.year == 2022, BaseField.name == name, Field.cultivations.any()).one_or_none()
    if db_field is None:
        return

    field = md.Field(db_field)
    plan = md.Plan(field)

    for db_cultivation in db_field.cultivations:
        crop = md.Crop(db_cultivation.crop, db_cultivation.crop_class)
        cultivation = md.Cultivation(db_cultivation, crop)
        plan.cultivations.append(cultivation)

    for db_fertilization in db_field.fertilizations:
        fertilizer = md.Fertilizer(db_fertilization.fertilizer)
        crop = md.Crop(
            db_fertilization.cultivation.crop, db_fertilization.cultivation.crop_class
        )
        fertilization = md.Fertilization(db_fertilization, fertilizer, crop, db_fertilization.cultivation.crop_class)
        plan.fertilizations.append(fertilization)

    # print(f"Start timing:", plan.field.Field.base_field.name)
    # start_time = time()

    field_demand = plan.sum_demands()
    field_reduction = plan.sum_reductions()
    field_fert = plan.sum_fertilizations()

    # print(f"Finished in {time() - start_time:.2f} secs")


if __name__ == "__main__":
    # reseed_database()
    # plans = data_collection(end=3, year=2021)
    # for plan in plans:
    #     visualize_plan(plan=plan)
    # log_error(index=None, plans=None, visual=False)
    # timing(header=5)
    small_timing(name="Am Jammer")
