import timeit
from decimal import Decimal

from database.setup import setup_database
from database.types import *
from model import *
from utils import load_json

# seed = load_json("data/schläge_reversed.json")
# setup_database("database2.db", seed)

# print(SoilType(SoilType.clayey_loam_to_clay).value)


def main():
    feld = Field()
    frucht = Crop(
        crop_class=CropClass.main_crop,
    )
    dünger = Fertilizer(fert_class=FertClass.organic, fert_type=FertType.digestate, n=Decimal("5"))

    düngung = Fertilization(MeasureType.fall, Decimal("10"), feld, dünger, frucht)
    nges = düngung.nges(measure=MeasureType.spring, crop_class=CropClass.main_crop, netto=True)
    return nges


if __name__ == "__main__":
    print(main())
