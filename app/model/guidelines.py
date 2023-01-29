from functools import cache

from loguru import logger

from app.utils import load_json


@cache
def p2o5_reductions():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Abschläge/abschlag_p2o5.json")


@cache
def k2o_reductions():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Abschläge/abschlag_k2o.json")


@cache
def mg_reductions():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Abschläge/abschlag_mgo.json")


@cache
def cao_reductions():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Abschläge/abschlag_cao_4jahre.json")


@cache
def sulfur_reductions():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Abschläge/abschlag_s.json")


@cache
def soil_reductions():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Abschläge/bodenvorrat.json")


@cache
def p2o5_classes():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Gehaltsklassen/klassen_p2o5.json")


@cache
def k2o_classes():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Gehaltsklassen/klassen_k2o.json")


@cache
def mg_classes():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Gehaltsklassen/klassen_mgo.json")


@cache
def ph_classes():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Gehaltsklassen/klassen_ph_wert.json")


@cache
def org_factor():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Abschläge/wirkungsfaktoren.json")


@cache
def pre_crop_effect():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Abschläge/vorfrucht.json")


@cache
def legume_delivery():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Abschläge/leguminosen.json")


@cache
def sulfur_needs():
    logger.info("Caching data")
    return load_json("data/Richtwerte/Nährstoffwerte/schwefelbedarf.json")
