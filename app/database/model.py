import enum

from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship


class CropType(enum.Enum):
    # Hauptfrüchte
    rotating_fallow_with_legume = "Rotationsbrache mit Leguminosen"
    rotating_fallow = "Rotationsbrache ohne Leguminosen"
    permanent_fallow = "Dauerbrache"
    permanent_grassland = "Dauergrünland"
    alfalfa = "Luzerne"
    alfalfa_grass = "Luzernegras"
    clover = "Klee"
    clover_grass = "Kleegras"
    sugar_beets = "Zuckerrüben"
    canola = "Raps"
    legume_grain = "Körnerleguminosen"
    cabbage = "Kohlgemüse"
    field_grass = "Acker-/Saatgras"
    grain = "Getreide"
    corn = "Mais"
    potato = "Kartoffel"
    vegetable = "Gemüse ohne Kohlarten"
    # Zwischenfrüchte
    non_legume = "Nichtleguminosen"
    legume = "Leguminosen"
    other_catch_crop = "andere Zwischenfrüchte"


class CropClass(enum.Enum):
    catch_crop = "Zwischenfrucht"
    main_crop = "Hauptfrucht"
    second_crop = "Zweitfrucht"
    first_cut = "1. Schnitt"
    second_cut = "2. Schnitt"
    third_cut = "3. Schnitt"
    fourth_cut = "4. Schnitt"


class RemainsType(enum.Enum):
    # Hauptfrüchte
    remains = "verbleibt"
    no_remains = "abgefahren"
    # Zwischenfrüchte
    frozen = "abgefroren"
    not_frozen_fall = "nicht abgf., eing. Herbst"
    not_frozen_spring = "nicht abgf., eing. Frühjahr"


class FieldType(enum.Enum):
    grassland = "Grünland"
    cropland = "Ackerland"
    exchanged_land = "Tauschfläche"
    fallow_grassland = "Ackerland-Brache"
    fallow_cropland = "Grünland-Brache"


class MeasureType(enum.Enum):
    fall = "Herbst"
    spring = "Frühjahr"
    first_first_n_fert = "1.1 N-Gabe"
    first_second_n_fert = "1.2 N-Gabe"
    first_n_fert = "1. N-Gabe"
    second_n_fert = "2. N-Gabe"
    third_n_fert = "3. N-Gabe"
    fourth_n_fert = "4. N-Gabe"
    first_base_fert = "1. Grundd."
    second_base_fert = "2. Grundd."
    third_base_fert = "3. Grundd."
    fourth_base_fert = "4. Grundd."
    lime_fert = "Kalkung"
    misc_fert = "Sonstige"


class SoilType(enum.Enum):
    sand = "Sand"
    light_loamy_sand = "schwach lehmiger Sand"
    strong_loamy_sand = "stark lehmiger Sand"
    sandy_to_silty_loam = "sand. bis schluff. Lehm"
    clayey_loam_to_clay = "toniger Lehm bis Ton"
    moor = "Niedermoor"


class HumusType(enum.Enum):
    less_4 = r"< 4%"
    less_8 = r"4% bis < 8%"
    less_15 = r"8% bis < 15%"
    less_30 = r"15% bis < 30%"
    more_30 = r">= 30%"


class FertClass(enum.Enum):
    organic = "Wirtschaftsdünger"
    mineral = "Mineraldünger"


class FertType(enum.Enum):
    # organic
    digestate = "Gärrest"
    slurry = "Gülle"
    manure = "Festmist"
    dry_manure = "Trockenmist"
    compost = "Kompost"
    # mineral
    k = "K"
    n = "N"
    n_k = "N/K"
    n_p = "N/P"
    n_s = "N+S"
    n_p_k = "NPK"
    n_p_k_s = "NPKS"
    p = "P"
    p_k = "P/K"
    lime = "Kalk"
    misc = "Sonstige"
    auxiliary = "Hilfsstoffe"


Base = declarative_base()

field_fertilization = Table(
    "field_fertilization",
    Base.metadata,
    Column("field_id", Integer, ForeignKey("field.field_id")),
    Column("fertilization_id", Integer, ForeignKey("fertilization.fertilization_id")),
)


class Field(Base):
    __tablename__ = "field"
    id = Column("field_id", Integer, primary_key=True)
    prefix = Column("prefix", Integer)
    suffix = Column("suffix", Integer)
    name = Column("name", String)
    area = Column("area", Float(asdecimal=True))
    year = Column("year", Integer)
    type = Column("type", Enum(FieldType))
    cultivation = relationship("Cultivation", back_populates="field")
    fertilizations = relationship(
        "Fertilization",
        secondary=field_fertilization,
        back_populates="fields",
    )

    __table_args__ = (UniqueConstraint("prefix", "suffix", "year", name="active_fields"),)

    def __repr__(self):
        return (
            f"Field(id='{self.id}', name='{self.prefix:02d}-{self.suffix} {self.name}', "
            f"ha='{self.area:.2f}', type='{self.type.name}', "
            f"cultivations={[f'{cult.crop_class.name}: {cult.crop.name}' for cult in self.cultivation]}, "
            f"fertilizations={[f'{fert.measure.name} -> {fert.cultivation.crop.name}: {fert.fertilizer.name}' for fert in self.fertilizations]})"
        )


class Cultivation(Base):
    __tablename__ = "cultivation"
    id = Column("cultivation_id", Integer, primary_key=True)
    field_id = Column("field_id", Integer, ForeignKey("field.field_id"))
    crop_class = Column("crop_class", Enum(CropClass))
    crop_id = Column("crop_id", Integer, ForeignKey("crop.crop_id"))
    crop_yield = Column("yield", Float(asdecimal=True))
    remains = Column("remains", Enum(RemainsType))
    legume_rate = Column("legume_rate", String)
    field = relationship("Field", back_populates="cultivation")
    crop = relationship("Crop", backref=backref("cultivation"))

    __table_args__ = (UniqueConstraint("field_id", "crop_class", name="active_crops"),)

    def __repr__(self):
        return (
            f"Cultivation(id='{self.id}', field='{self.field.name}', year='{self.year}', type='{self.crop_type.name}', "
            f"name='{self.crop.name}', yield='{self.crop_yield:.2f}', field='{self.fields[0].name}')"
        )


class Fertilization(Base):
    __tablename__ = "fertilization"
    id = Column("fertilization_id", Integer, primary_key=True)
    cultivation_id = Column("cultivation_id", Integer, ForeignKey("cultivation.cultivation_id"))
    fertilizer_id = Column("fertilizer_id", Integer, ForeignKey("fertilizer.fertilizer_id"))
    amount = Column("amount", Float(asdecimal=True))
    measure = Column("measure", Enum(MeasureType))
    month = Column("month", Integer)
    fields = relationship(
        "Field",
        secondary=field_fertilization,
        back_populates="fertilizations",
    )
    cultivation = relationship("Cultivation", backref=backref("fertilization"))
    fertilizer = relationship("Fertilizer", backref=backref("fertilization"))

    def __repr__(self):
        return (
            f"Fertilization(id='{self.id}', name='{self.fertilizer.name}', amount='{self.amount:.2f}', "
            f"measure='{self.measure.name}', month='{self.month}', crop='{self.cultivation.crop.name}')"
        )


class Crop(Base):
    __tablename__ = "crop"
    id = Column("crop_id", Integer, primary_key=True)
    name = Column("name", String, unique=True)
    crop_type = Column("type", Enum(CropType))  # used for pre-crop effect

    def __repr__(self):
        return f"Crop(id='{self.id}', name='{self.name}', type='{self.crop_type}')"


class Fertilizer(Base):
    __tablename__ = "fertilizer"
    id = Column("fertilizer_id", Integer, primary_key=True)
    name = Column("name", String)
    year = Column("year", Integer)
    fert_class = Column("class", Enum(FertClass))
    fert_type = Column("type", Enum(FertType))
    active = Column("active", Boolean, nullable=True)
    usage = relationship("FertilizerUsage", backref="fertilizer")

    __table_args__ = (UniqueConstraint("name", "year", name="fertilizers"),)

    def __repr__(self):
        return (
            f"Fertilizer(id='{self.id}', name='{self.name}', year='{self.year}', "
            f"class='{self.fert_class.name}', type='{self.fert_type.name}', active='{self.active}', "
            f"usage={[f'{usage.year}: {usage.amount:.2f}' for usage in self.usage]}')"
        )


class FertilizerUsage(Base):
    __tablename__ = "fertilizer_usage"
    id = Column("id", Integer, primary_key=True)
    name = Column("fertilizer_name", String, ForeignKey("fertilizer.name"))
    year = Column("year", Integer)
    amount = Column("amount", Float(asdecimal=True))

    __table_args__ = (UniqueConstraint("fertilizer_name", "year"),)

    def __repr__(self):
        return (
            f"FertilizerUsage(name='{self.name}', year='{self.year}', amount='{self.amount:.2f}')"
        )


class SoilSample(Base):
    __tablename__ = "soil_sample"
    id = Column("sample_id", Integer, primary_key=True)
    field_id = Column("field_id", Integer, ForeignKey("field.field_id"))
    date = Column("date", Integer)
    ph = Column("ph", Float(asdecimal=True))
    p2o5 = Column("p2o5", Float(asdecimal=True))
    k2o = Column("k2o", Float(asdecimal=True))
    mg = Column("mg", Float(asdecimal=True))
    soil_type = Column("soil_type", Enum(SoilType))
    humus = Column("humus", Enum(HumusType))
    field = relationship("Field", backref=backref("soil_sample"))

    def __repr__(self):
        return (
            f"SoilSample(id='{self.id}', fields='{self.field.name}', year='{self.year}', "
            f"soil_type='{self.soil_type.name}', humus='{self.humus.name}')"
        )
