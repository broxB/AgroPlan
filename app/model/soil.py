from dataclasses import dataclass
from decimal import Decimal

from database.model import SoilSample
from database.types import HumusType, SoilType
from utils import load_json


@dataclass
class Soil:
    soil_sample: SoilSample

    def __post_init__(self):
        self.year = self.soil_sample.year
        self.type: SoilType = self.soil_sample.soil_type  # schwach lehmiger Sand
        self.humus: HumusType = self.soil_sample.humus  # < 4%
        self.ph = self.soil_sample.ph
        self.p2o5 = self.soil_sample.p2o5
        self.k2o = self.soil_sample.k2o
        self.mg = self.soil_sample.mg
        self.s_reduction = load_json("data/Richtwerte/Abschläge/abschlag_s.json")
        self.p2o5_reduction = load_json("data/Richtwerte/Abschläge/abschlag_p2o5.json")
        self.k2o_reduction = load_json("data/Richtwerte/Abschläge/abschlag_k2o.json")
        self.mgo_reduction = load_json("data/Richtwerte/Abschläge/abschlag_mgo.json")
        self.cao_reduction = load_json("data/Richtwerte/Abschläge/abschlag_cao_4jahre.json")
        self.soil_reduction = load_json("data/Richtwerte/Abschläge/bodenvorrat.json")
        self.previous_crop = load_json("data/Richtwerte/Abschläge/vorfrucht.json")
