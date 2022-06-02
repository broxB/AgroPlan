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


class CropType(enum.IntEnum):
    catch_crop = 1  # Zwischenfrucht
    main_crop = 2  # Hauptfrucht
    second_crop = 3  # Zweitfrucht


class RemainsType(enum.IntEnum):
    remains = 1
    no_remains = 2
    frozen = 3
    not_frozen_fall = 4
    not_frozen_spring = 5


class FieldType(enum.IntEnum):
    grassland = 1
    cropland = 2
    grass_fallowland = 3
    crop_fallowland = 4


class MeasureType(enum.IntEnum):
    fall = 1
    spring = 2
    first_first_n_fert = 10
    first_second_n_fert = 11
    first_n_fert = 12
    second_n_fert = 13
    third_n_fert = 14
    fourth_n_fert = 15
    first_base_fert = 16
    second_base_fert = 17
    third_base_fert = 18
    fourth_base_fert = 19
    lime_fert = 20
    misc_fert = 21


class SoilType(enum.IntEnum):
    sand = 1
    light_loamy_sand = 2
    strong_loamy_sand = 3
    sandy_to_silty_loam = 4
    clayey_loam_to_clay = 5
    moor = 6


class HumusType(enum.IntEnum):
    less_4 = 1
    less_8 = 2
    less_15 = 3
    less_30 = 4
    more_30 = 5


class FertClass(enum.IntEnum):
    organic = 1
    mineral = 2


class FertType(enum.IntEnum):
    # organic
    digestate = 1
    slurry = 2
    manure = 3
    dry_manure = 4
    compost = 5
    # mineral
    K = 10
    N = 11
    N_K = 12
    N_P = 13
    N_S = 14
    N_P_K = 15
    N_P_K_S = 16
    P = 17
    P_K = 18
    lime = 19  # Kalk
    misc = 20  # Sonstige


Base = declarative_base()

field_cultivation = Table(
    "field_cultivation",
    Base.metadata,
    Column("field_id", Integer, ForeignKey("field.field_id")),
    Column("cultivation_id", Integer, ForeignKey("cultivation.cultivation_id")),
)

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
    type = Column("type", Enum(FieldType))
    cultivations = relationship(
        "Cultivation",
        secondary=field_cultivation,
        back_populates="fields",
    )
    fertilizations = relationship(
        "Fertilization",
        secondary=field_fertilization,
        back_populates="fields",
    )

    __table_args__ = (UniqueConstraint("prefix", "suffix", "name", "area", "type", name="active_fields"),)

    def __repr__(self):
        return (
            f"Field(id='{self.id}', name='{self.prefix:02d}-{self.suffix} {self.name}', "
            f"ha='{self.area:.2f}', type='{self.type.name}', "
            f"cultivations={[f'{cult.crop_type.name}: {cult.crop.name}' for cult in self.cultivations]}, "
            f"fertilizations={[f'{fert.measure.name} -> {fert.cultivation.crop.name}: {fert.fertilizer.name}' for fert in self.fertilizations]})"
        )


class Cultivation(Base):
    __tablename__ = "cultivation"
    id = Column("cultivation_id", Integer, primary_key=True)
    year = Column("year", Integer)
    crop_type = Column("crop_type", Enum(CropType))
    crop_id = Column("crop_id", Integer, ForeignKey("crop.crop_id"))
    crop_yield = Column("yield", Float(asdecimal=True))
    remains = Column("remains", Enum(RemainsType))
    legume_rate = Column("legume_rate", String)
    fields = relationship(
        "Field",
        secondary=field_cultivation,
        back_populates="cultivations",
    )
    crop = relationship("Crop", backref=backref("cultivation"))

    __table_args__ = (UniqueConstraint("year", "crop_type", name="active_crops"),)

    def __repr__(self):
        return (
            f"Cultivation(id='{self.id}', year='{self.year}', type='{self.crop_type.name}', "
            f"name='{self.crop.name}', yield='{self.crop_yield:.2f}', field='{self.fields[0].name}')"
        )


class Fertilization(Base):
    __tablename__ = "fertilization"
    id = Column("fertilization_id", Integer, primary_key=True)
    cultivation_id = Column(
        "cultivation_id", Integer, ForeignKey("cultivation.cultivation_id")
    )
    fertilizer_id = Column(
        "fertilizer_id", Integer, ForeignKey("fertilizer.fertilizer_id")
    )
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
    crop_type = Column("type", String)

    def __repr__(self):
        return f"Crop(id='{self.id}', name='{self.name}', type='{self.crop_type}')"


class Fertilizer(Base):
    __tablename__ = "fertilizer"
    id = Column("fertilizer_id", Integer, primary_key=True)
    name = Column("name", String, unique=True)
    year = Column("year", Integer)
    fert_class = Column("class", Enum(FertClass))
    fert_type = Column("type", Enum(FertType))
    active = Column("active", Boolean, nullable=True)

    def __repr__(self):
        return (
            f"Fertilizer(id='{self.id}', name='{self.name}', year='{self.year}', "
            f"class='{self.fert_class.name}', type='{self.fert_type.name}', active='{self.active}')"
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
