import logging
from decimal import Decimal

import pytest

from app.app import create_app
from app.database.model import (
    BaseField,
    Crop,
    Cultivation,
    Fertilization,
    Fertilizer,
    Field,
    Modifier,
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
    NutrientType,
    ResidueType,
    SoilType,
    UnitType,
)
from app.extensions import db as _db
from config import TestConfig

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def app():
    logger.info("creating app")
    app = create_app(config_object=TestConfig)
    return app


@pytest.fixture(scope="session")
def client(app):
    logger.info("creating app-context")
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def db(client):
    logger.info("creating db")
    _db.create_all()
    yield _db
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user() -> User:
    user = User(id=1, username="Test", email="test@test.test")
    user.set_password("ValidPassword")
    user.year = 1000
    return user


@pytest.fixture
def base_field(user) -> BaseField:
    base_field = BaseField(id=1, user_id=user.id, prefix=1, suffix=0, name="Testfield")
    return base_field


@pytest.fixture
def field_first_year(base_field) -> Field:
    field = Field(
        id=1,
        base_id=base_field.id,
        sub_suffix=1,
        area=Decimal("11.11"),
        year=1000,
        red_region=False,
        field_type=FieldType.cropland,
        demand_p2o5=DemandType.demand,
        demand_k2o=DemandType.demand,
        demand_mgo=DemandType.demand,
    )
    return field


@pytest.fixture
def field_second_year(base_field) -> Field:
    field = Field(
        id=2,
        base_id=base_field.id,
        sub_suffix=1,
        area=Decimal("11.11"),
        year=1001,
        red_region=False,
        field_type=FieldType.cropland,
        demand_p2o5=DemandType.demand,
        demand_k2o=DemandType.demand,
        demand_mgo=DemandType.demand,
    )
    return field


@pytest.fixture
def field_grass(user) -> Crop:
    crop = Crop(
        id=1,
        user_id=user.id,
        name="Ackergras 3 Schnitte",
        field_type=FieldType.cropland,
        crop_class=CropClass.main_crop,
        crop_type=CropType.field_grass,
        kind="Ackergras",
        feedable=True,
        residue=False,
        nmin_depth=NminType.nmin_0,
        target_demand=1,
        target_yield=1,
        pos_yield=1,
        neg_yield=1,
        target_protein=1,
        var_protein=1,
        p2o5=1,
        k2o=1,
        mgo=1,
        byproduct="Heu",
        byp_ratio=1,
        byp_n=1,
        byp_p2o5=1,
        byp_k2o=1,
        byp_mgo=1,
    )
    return crop


@pytest.fixture
def corn(user) -> Crop:
    corn = Crop(
        id=2,
        user_id=user.id,
        name="Silomais 32%",
        field_type=FieldType.cropland,
        crop_class=CropClass.main_crop,
        crop_type=CropType.corn,
        kind="Mais",
        feedable=False,
        residue=False,
        nmin_depth=NminType.nmin_90,
        target_demand=250,
        target_yield=450,
        pos_yield=Decimal(1),
        neg_yield=Decimal("1.5"),
        p2o5=Decimal(1),
        k2o=Decimal(1),
        mgo=Decimal(1),
    )
    return corn


@pytest.fixture
def mustard(user) -> Crop:
    mustard = Crop(
        id=4,
        user_id=user.id,
        name="Senf (GP)",
        field_type=FieldType.cropland,
        crop_class=CropClass.second_crop,
        crop_type=CropType.legume_grain,
        kind="Gelbsenf",
        feedable=False,
        residue=False,
        nmin_depth=NminType.nmin_60,
        target_demand=130,
        target_yield=200,
        pos_yield=Decimal(1),
        neg_yield=Decimal("1.5"),
        p2o5=Decimal("2.36"),
        k2o=Decimal("4.69"),
        mgo=Decimal("0.51"),
    )
    return mustard


@pytest.fixture
def catch_crop(user) -> Crop:
    catch_crop = Crop(
        id=3,
        user_id=user.id,
        name="Zwischenfrucht",
        field_type=FieldType.cropland,
        crop_class=CropClass.catch_crop,
        crop_type=CropType.catch_non_legume,
        kind="Nichtleguminosen",
        feedable=False,
        residue=True,
        nmin_depth=NminType.nmin_0,
        target_demand=60,
        target_yield=0,
        pos_yield=Decimal(0),
        neg_yield=Decimal(0),
    )
    return catch_crop


@pytest.fixture
def cultivation_field_grass(field_grass) -> Cultivation:
    cultivation = Cultivation(
        cultivation_type=CultivationType.main_crop,
        crop_id=field_grass.id,
        crop_yield=1,
        crop_protein=1,
        residues=ResidueType.none,
        legume_rate=LegumeType.none,
        nmin_30=1,
        nmin_60=1,
        nmin_90=2,
    )
    return cultivation


@pytest.fixture
def cultivation_mustard(mustard) -> Cultivation:
    cultivation = Cultivation(
        cultivation_type=CultivationType.second_crop,
        crop_id=mustard.id,
        crop_yield=180,
        residues=ResidueType.none,
        nmin_30=10,
        nmin_60=10,
        nmin_90=10,
    )
    return cultivation


@pytest.fixture
def cultivation_corn(corn) -> Cultivation:
    cultivation = Cultivation(
        cultivation_type=CultivationType.main_crop,
        crop_id=corn.id,
        crop_yield=300,
        residues=ResidueType.none,
        nmin_30=10,
        nmin_60=10,
        nmin_90=10,
    )
    return cultivation


@pytest.fixture
def cultivation_catch(catch_crop) -> Cultivation:
    cultivation = Cultivation(
        cultivation_type=CultivationType.catch_crop,
        crop_id=catch_crop.id,
        crop_yield=0,
        residues=ResidueType.catch_frozen,
    )
    return cultivation


@pytest.fixture
def organic_fertilizer(user) -> Fertilizer:
    fertilizer = Fertilizer(
        id=1,
        user_id=user.id,
        name="Gärrest 1000",
        year=1000,
        fert_class=FertClass.organic,
        fert_type=FertType.org_digestate,
        active=True,
        unit=UnitType.cbm,
        price=Decimal(100),
        n=Decimal(1),
        p2o5=Decimal(1),
        k2o=Decimal(1),
        mgo=Decimal(1),
        s=Decimal(1),
        cao=Decimal(1),
        nh4=Decimal(1),
    )
    return fertilizer


@pytest.fixture
def mineral_fertilizer(user) -> Fertilizer:
    fertilizer = Fertilizer(
        id=2,
        user_id=user.id,
        name="Mineral Fertilizer",
        fert_class=FertClass.mineral,
        fert_type=FertType.n,
        active=True,
        unit=UnitType.dt,
        price=Decimal(50),
        n=Decimal(2),
        p2o5=Decimal(2),
        k2o=Decimal(2),
        mgo=Decimal(2),
        s=Decimal(2),
        cao=Decimal(2),
        nh4=Decimal(2),
    )
    return fertilizer


@pytest.fixture
def organic_fertilizer_second_year(user) -> Fertilizer:
    fertilizer = Fertilizer(
        id=3,
        user_id=user.id,
        name="Gärrest 1001",
        year=1001,
        fert_class=FertClass.organic,
        fert_type=FertType.org_digestate,
        active=True,
        unit=UnitType.cbm,
        price=Decimal(100),
        n=Decimal(10),
        p2o5=Decimal(2),
        k2o=Decimal(2),
        mgo=Decimal(2),
        s=Decimal(2),
        cao=Decimal(2),
        nh4=Decimal(2),
    )
    return fertilizer


@pytest.fixture
def organic_fertilization(organic_fertilizer) -> Fertilization:
    fertilization = Fertilization(
        fertilizer_id=organic_fertilizer.id,
        cut_timing=CutTiming.none,
        amount=Decimal(10),
        measure=MeasureType.org_fall,
        month=10,
    )
    return fertilization


@pytest.fixture
def organic_fertilization_second_year(organic_fertilizer_second_year) -> Fertilization:
    fertilization = Fertilization(
        fertilizer_id=organic_fertilizer_second_year.id,
        cut_timing=CutTiming.none,
        amount=Decimal(10),
        measure=MeasureType.org_fall,
        month=10,
    )
    return fertilization


@pytest.fixture
def mineral_fertilization(mineral_fertilizer) -> Fertilization:
    fertilization = Fertilization(
        fertilizer_id=mineral_fertilizer.id,
        cut_timing=CutTiming.none,
        amount=Decimal(3),
        measure=MeasureType.first_n_fert,
    )
    return fertilization


@pytest.fixture
def soil_sample(base_field) -> SoilSample:
    soil_sample = SoilSample(
        id=1,
        base_id=base_field.id,
        year=1000,
        ph=Decimal(1),
        p2o5=Decimal(1),
        k2o=Decimal(1),
        mg=Decimal(1),
        soil_type=SoilType.sand,
        humus=HumusType.less_8,
    )
    return soil_sample


@pytest.fixture
def modifier(field_first_year: Field) -> Modifier:
    modifier = Modifier(
        id=1,
        field_id=field_first_year.id,
        description="Test mod",
        modification=NutrientType.n,
        amount=10,
    )
    return modifier


@pytest.fixture
def saldo(field_first_year) -> Saldo:
    saldo = Saldo(
        field_id=field_first_year.id,
        n=Decimal(1),
        p2o5=Decimal(1),
        k2o=Decimal(1),
        mgo=Decimal(1),
        s=Decimal(1),
        cao=Decimal(1),
        n_total=Decimal(1),
    )
    return saldo


@pytest.fixture
def fill_db(
    db,
    user,
    base_field,
    field_first_year,
    field_second_year,
    field_grass,
    corn,
    mustard,
    catch_crop,
    organic_fertilizer,
    organic_fertilizer_second_year,
    mineral_fertilizer,
    cultivation_field_grass,
    cultivation_corn,
    cultivation_mustard,
    cultivation_catch,
    organic_fertilization,
    organic_fertilization_second_year,
    mineral_fertilization,
    soil_sample,
    modifier,
    saldo,
):
    db.session.add(user)
    db.session.add(base_field)
    db.session.add(soil_sample)
    db.session.add(field_grass)
    db.session.add(corn)
    db.session.add(mustard)
    db.session.add(catch_crop)
    db.session.add(organic_fertilizer)
    db.session.add(organic_fertilizer_second_year)
    db.session.add(mineral_fertilizer)

    # first year
    db.session.add(field_first_year)

    # 1. cultivaiton
    cultivation_field_grass.field = field_first_year
    db.session.add(cultivation_field_grass)
    # 1. fertilization
    organic_fertilization.field = field_first_year
    organic_fertilization.cultivation = cultivation_field_grass
    db.session.add(organic_fertilization)

    db.session.add(saldo)

    # second year
    db.session.add(field_second_year)

    # catch cultivation
    cultivation_catch.field = field_second_year
    db.session.add(cultivation_catch)
    # 1. fertilization
    organic_fertilization_second_year.field = field_second_year
    organic_fertilization_second_year.cultivation = cultivation_catch
    db.session.add(organic_fertilization_second_year)
    # main cultivation
    cultivation_corn.field = field_second_year
    db.session.add(cultivation_corn)
    # 2. fertilization
    mineral_fertilization.field = field_second_year
    mineral_fertilization.cultivation = cultivation_corn
    db.session.add(mineral_fertilization)
    # second cultivation
    cultivation_mustard.field = field_second_year
    db.session.add(cultivation_mustard)

    db.session.add(modifier)

    db.session.commit()


@pytest.fixture
def guidelines() -> object:
    class guidelines:
        """
        Fixture to pull guidelines from.
        """

        @staticmethod
        def soil_reductions():
            return {
                HumusType.less_4.value: {
                    FieldType.cropland.value: 0,
                    FieldType.grassland.value: 10,
                }
            }

        @staticmethod
        def p2o5_reductions():
            return {
                FieldType.cropland.value: {
                    "Werte": [0.0, 1.4, 3.1, 4.4, 5.6, 6.9, 8.1, 9.5, 11.0],
                    "Abschläge": [-69, -46, -34, -23, 0, 34, 57, 80, "inf"],
                },
                FieldType.grassland.value: {
                    "Werte": [0.0, 1.4, 3.1, 4.4, 5.6, 6.9, 8.1, 9.5, 11.0],
                    "Abschläge": [-46, -34, -23, -11, 0, 23, 46, 69, "inf"],
                },
            }

        @staticmethod
        def k2o_reductions():
            return {
                FieldType.cropland.value: {
                    SoilType.sand.value: {
                        HumusType.less_4.value: {
                            "Werte": [0, 2, 4, 5.6, 7, 9, 11, 13.6, 15.1],
                            "Abschläge": [-72, -60, -48, -36, -18, 0, 12, 24, "inf"],
                        }
                    }
                },
                FieldType.grassland.value: {
                    SoilType.sand.value: {
                        HumusType.less_4.value: {
                            "Werte": [0, 1.6, 3, 4.6, 6, 8.6, 11, 14, 18.1],
                            "Abschläge": [-48, -36, -24, -12, 0, 0, 30, 60, "inf"],
                        }
                    }
                },
            }

        @staticmethod
        def mg_reductions():
            return {
                FieldType.cropland.value: {
                    SoilType.sand.value: {
                        HumusType.less_4.value: {
                            "Werte": [0, 2, 4, 5, 6, 7.6, 9, 9.6, 10.1],
                            "Abschläge": [-50, -41, -33, -25, -8, 0, 0, "inf", "inf"],
                        }
                    }
                },
                FieldType.grassland.value: {
                    SoilType.sand.value: {
                        HumusType.less_4.value: {
                            "Werte": [0, 2, 4, 5, 6, 7.6, 9, 9.6, 10.1],
                            "Abschläge": [-50, -41, -33, -25, -8, 0, 0, "inf", "inf"],
                        }
                    }
                },
            }

        @staticmethod
        def sulfur_reductions():
            return {
                "Grenzwerte": {"Bedarf": [0, 20, 30, 40], "Nges": [0, 100, 201]},
                "Humusgehalt": {HumusType.less_4.value: [0, 0, 0, 0]},
                "Nges": {"0": [0, 0, 0, 0], "100": [0, 10, 10, 10], "201": [0, 20, 20, 20]},
            }

        @staticmethod
        def cao_reductions():
            return {
                FieldType.cropland.value: {
                    "phWert": [
                        3,
                        3.1,
                        3.2,
                        3.3,
                        3.4,
                        3.5,
                        3.6,
                        3.7,
                        3.8,
                        3.9,
                        4.0,
                        4.1,
                        4.2,
                        4.3,
                        4.4,
                        4.5,
                        4.6,
                        4.7,
                        4.8,
                        4.9,
                        5.0,
                        5.1,
                        5.2,
                        5.3,
                        5.4,
                        5.5,
                        5.6,
                        5.7,
                        5.8,
                        5.9,
                        6.0,
                        6.1,
                        6.2,
                        6.3,
                        6.4,
                        6.5,
                        6.6,
                        6.7,
                        6.8,
                        6.9,
                        7.0,
                        7.1,
                        7.2,
                        7.3,
                    ],
                    SoilType.sand.value: {
                        HumusType.less_4.value: [
                            45,
                            45,
                            45,
                            45,
                            45,
                            45,
                            45,
                            45,
                            45,
                            45,
                            45,
                            42,
                            39,
                            36,
                            33,
                            30,
                            27,
                            24,
                            22,
                            19,
                            16,
                            13,
                            10,
                            7,
                            6,
                            6,
                            6,
                            6,
                            6,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                        ]
                    },
                },
                FieldType.grassland.value: {
                    "phWert": [
                        3.0,
                        3.1,
                        3.2,
                        3.3,
                        3.4,
                        3.5,
                        3.6,
                        3.7,
                        3.8,
                        3.9,
                        4.0,
                        4.1,
                        4.2,
                        4.3,
                        4.4,
                        4.5,
                        4.6,
                        4.7,
                        4.8,
                        4.9,
                        5.0,
                        5.1,
                        5.2,
                        5.3,
                        5.4,
                        5.5,
                        5.6,
                        5.7,
                        5.8,
                        5.9,
                        6.0,
                        6.1,
                        6.2,
                        6.3,
                        6.4,
                        6.5,
                        6.6,
                    ],
                    SoilType.sand.value: {
                        HumusType.less_4.value: [
                            30,
                            30,
                            30,
                            30,
                            30,
                            30,
                            28,
                            25,
                            23,
                            21,
                            19,
                            16,
                            14,
                            12,
                            9,
                            7,
                            5,
                            4,
                            4,
                            4,
                            4,
                            4,
                            4,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                        ]
                    },
                },
            }

        @staticmethod
        def p2o5_classes():
            return {
                FieldType.cropland.value: [0, 3.1, 5.6, 8.1, 11],
                FieldType.grassland.value: [0, 3.1, 5.6, 8.1, 11],
            }

        @staticmethod
        def k2o_classes():
            return {
                FieldType.cropland.value: {
                    SoilType.sand.value: {HumusType.less_4.value: [0, 3.1, 5.6, 8.1, 11]}
                },
                FieldType.grassland.value: {
                    SoilType.sand.value: {HumusType.less_4.value: [0, 3, 6, 11, 18.1]}
                },
            }

        @staticmethod
        def mg_classes():
            return {
                FieldType.cropland.value: {
                    SoilType.sand.value: {HumusType.less_4.value: [0, 4, 6, 9, 10.1]}
                },
                FieldType.grassland.value: {
                    SoilType.sand.value: {HumusType.less_4.value: [0, 4, 6, 9, 10.1]}
                },
            }

        @staticmethod
        def ph_classes():
            return {
                FieldType.cropland.value: {
                    SoilType.sand.value: {HumusType.less_4.value: [0, 4.6, 5.4, 5.9, 6.3]}
                },
                FieldType.grassland.value: {
                    SoilType.sand.value: {HumusType.less_4.value: [0, 4.1, 4.7, 5.3, 5.7]}
                },
            }

        @staticmethod
        def org_factor():
            return {
                FertType.org_digestate.value: {
                    "Lagerverluste": 0.5,
                    FieldType.cropland.value: 0.6,
                    FieldType.grassland.value: 0.5,
                }
            }

        @staticmethod
        def pre_crop_effect():
            return {CropType.field_grass.value: 10}

        @staticmethod
        def legume_delivery():
            return {
                FieldType.grassland.value: {
                    LegumeType.grass_less_5.value: 0,
                    LegumeType.grass_less_10.value: 20,
                    LegumeType.grass_less_20.value: 40,
                    LegumeType.grass_greater_20.value: 60,
                },
                CropType.clover_grass.value: 30,
                CropType.alfalfa_grass.value: 30,
                CropType.clover.value: 360,
                CropType.alfalfa.value: 360,
            }

        @staticmethod
        def sulfur_needs():
            return {
                "W.-Roggen": 20,
                "So.-Gerste": 20,
                "Silomais 32%": 20,
                "Nichtleguminosen": 20,
                "Ackergras 3 Schnitte": 20,
                "W.-Gerste": 30,
                "Wiese 4 Schnitte": 30,
            }

    return guidelines
