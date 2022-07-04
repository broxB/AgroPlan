from database.types import (
    CropClass,
    CropType,
    DemandType,
    FertClass,
    FertType,
    FieldType,
    HumusType,
    LegumeType,
    MeasureType,
    RemainsType,
    SoilType,
    UnitType,
)
from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    Float,
    ForeignKey,
    Integer,
    PickleType,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import backref, relationship

__all__ = [
    "field_fertilization",
    "field_soil_sample",
    "BaseField",
    "Field",
    "Cultivation",
    "Crop",
    "Fertilization",
    "Fertilizer",
    "FertilizerUsage",
    "SoilSample",
]

Base = declarative_base()

field_fertilization = Table(
    "field_fertilization",
    Base.metadata,
    Column("field_id", Integer, ForeignKey("field.field_id")),
    Column("fertilization_id", Integer, ForeignKey("fertilization.fertilization_id")),
)

field_soil_sample = Table(
    "field_soil_sample",
    Base.metadata,
    Column("field_id", Integer, ForeignKey("field.field_id")),
    Column("sample_id", Integer, ForeignKey("soil_sample.sample_id")),
)


class BaseField(Base):
    __tablename__ = "base_field"
    __table_args__ = (UniqueConstraint("prefix", "suffix", name="unique_base_fields"),)

    id = Column("base_id", Integer, primary_key=True)
    prefix = Column("prefix", Integer)
    suffix = Column("suffix", Integer)
    name = Column("name", String)
    fields = relationship("Field", back_populates="base_field")

    def __repr__(self):
        return (
            f"BaseField(id='{self.id}', name='{self.prefix:02d}-{self.suffix} {self.name}', "
            f"fields='{[f'{field.year}: {field.field_type.value}, {field.area:.2f}ha' for field in self.fields]}'"
        )


class Field(Base):
    __tablename__ = "field"
    __table_args__ = (UniqueConstraint("sub_suffix", "base_id", "year", name="unique_fields"),)

    id = Column("field_id", Integer, primary_key=True)
    base_id = Column("base_id", Integer, ForeignKey("base_field.base_id"))
    sub_suffix = Column("sub_suffix", Integer, default=0)
    area = Column("area", Float(asdecimal=True))
    year = Column("year", Integer)
    red_region = Column("red_region", Boolean)
    field_type = Column("field_type", Enum(FieldType))
    demand_type = Column("demand_type", Enum(DemandType))
    base_field = relationship("BaseField", back_populates="fields")
    cultivations = relationship("Cultivation", back_populates="field")
    fertilizations = relationship(
        "Fertilization",
        secondary=field_fertilization,
        back_populates="field",
    )
    soil_samples = relationship("SoilSample", secondary=field_soil_sample, back_populates="fields")
    saldo = relationship("Saldo", back_populates="field", uselist=False)

    def __repr__(self):
        return (
            f"Field(id='{self.id}', name='{self.base_field.prefix:02d}-{self.base_field.suffix} {self.base_field.name}', "
            f"year='{self.year}', ha='{self.area:.2f}', type='{self.field_type.value}', "
            f"soil_samples='{[sample.year for sample in self.soil_samples]}', "
            f"cultivations={[f'{cult.crop_class.value}: {cult.crop.name}' for cult in self.cultivations]}, "
            f"fertilizations={[f'{fert.cultivation.crop.name}: {fert.measure.value} -> {fert.fertilizer.name}' for fert in self.fertilizations]})"
        )


class Cultivation(Base):
    __tablename__ = "cultivation"
    __table_args__ = (UniqueConstraint("field_id", "crop_class", name="unique_cultivations"),)

    id = Column("cultivation_id", Integer, primary_key=True)
    field_id = Column("field_id", Integer, ForeignKey("field.field_id"))
    crop_class = Column("crop_class", Enum(CropClass))
    crop_id = Column("crop_id", Integer, ForeignKey("crop.crop_id"))
    crop_yield = Column("yield", Float(asdecimal=True))
    crop_protein = Column("protein", Float(asdecimal=True))
    remains = Column("remains", Enum(RemainsType))
    legume_rate = Column("legume_rate", Enum(LegumeType))
    nmin = Column("nmin", MutableList.as_mutable(PickleType), default=[])
    field = relationship("Field", back_populates="cultivations")
    crop = relationship("Crop", back_populates="cultivations")

    def __repr__(self):
        return (
            f"Cultivation(id='{self.id}', field='{self.field.base_field.name}', year='{self.field.year}', "
            f"type='{self.crop_class.value}', name='{self.crop.name}', yield='{self.crop_yield:.2f}', "
            f"remains='{self.remains.value}', legume='{self.legume_rate.value}', nmin='{self.nmin}')"
        )


class Crop(Base):
    __tablename__ = "crop"
    id = Column("crop_id", Integer, primary_key=True)
    name = Column("name", String, unique=True)
    crop_class = Column("class", Enum(CropClass))
    crop_type = Column("type", Enum(CropType))  # used for pre-crop effect
    kind = Column("kind", String)
    feedable = Column("feedable", Boolean)
    remains = Column("remains", Boolean)
    legume_rate = Column("legume_rate", Enum(LegumeType))
    nmin_depth = Column("nmin_depth", Integer)
    target_demand = Column("target_demand", Float(asdecimal=True))
    target_yield = Column("target_yield", Float(asdecimal=True))
    var_yield = Column("var_yield", MutableList.as_mutable(PickleType), default=[])
    target_protein = Column("target_protein", Float(asdecimal=True))
    var_protein = Column("var_protein", Float(asdecimal=True))
    n = Column("n", Float(asdecimal=True))
    p2o5 = Column("p2o5", Float(asdecimal=True))
    k2o = Column("k2o", Float(asdecimal=True))
    mgo = Column("mgo", Float(asdecimal=True))
    byproduct = Column("byproduct", String)
    byp_ratio = Column("byp_ratio", Float(asdecimal=True))
    byp_n = Column("byp_n", Float(asdecimal=True))
    byp_p2o5 = Column("byp_p2o5", Float(asdecimal=True))
    byp_k2o = Column("byp_k2o", Float(asdecimal=True))
    byp_mgo = Column("byp_mgo", Float(asdecimal=True))
    cultivations = relationship("Cultivation", back_populates="crop")

    def __repr__(self):
        return (
            f"Crop(id='{self.id}', name='{self.name}', type='{self.crop_type}', "
            f"var_yield='{self.var_yield}')"
        )


class Fertilization(Base):
    __tablename__ = "fertilization"

    id = Column("fertilization_id", Integer, primary_key=True)
    cultivation_id = Column("cultivation_id", Integer, ForeignKey("cultivation.cultivation_id"))
    fertilizer_id = Column("fertilizer_id", Integer, ForeignKey("fertilizer.fertilizer_id"))
    amount = Column("amount", Float(asdecimal=True))
    measure = Column("measure", Enum(MeasureType))
    month = Column("month", Integer)
    field = relationship(
        "Field",
        secondary=field_fertilization,
        back_populates="fertilizations",
    )
    cultivation = relationship("Cultivation", backref=backref("fertilization"))
    fertilizer = relationship("Fertilizer", backref=backref("fertilization"))

    def __repr__(self):
        return (
            f"Fertilization(id='{self.id}', name='{self.fertilizer.name}', amount='{self.amount:.2f}', "
            f"measure='{self.measure.value}', month='{self.month}', crop='{self.cultivation.crop.name}', "
            f"field='{[field.base_field.name for field in self.field][0]}')"
        )


class Fertilizer(Base):
    __tablename__ = "fertilizer"
    __table_args__ = (UniqueConstraint("name", "year", name="unique_fertilizers"),)

    id = Column("fertilizer_id", Integer, primary_key=True)
    name = Column("name", String)
    year = Column("year", Integer)
    fert_class = Column("class", Enum(FertClass))
    fert_type = Column("type", Enum(FertType))
    active = Column("active", Boolean)
    unit = Column("unit", Enum(UnitType))
    price = Column("price", Float(asdecimal=True))
    n = Column("n", Float(asdecimal=True))
    p2o5 = Column("p2o5", Float(asdecimal=True))
    k2o = Column("k2o", Float(asdecimal=True))
    mgo = Column("mgo", Float(asdecimal=True))
    s = Column("s", Float(asdecimal=True))
    cao = Column("cao", Float(asdecimal=True))
    nh4 = Column("nh4", Float(asdecimal=True))
    usage = relationship("FertilizerUsage", backref="fertilizer")

    def __repr__(self):
        return (
            f"Fertilizer(id='{self.id}', name='{self.name}', year='{self.year}', "
            f"class='{self.fert_class.name}', type='{self.fert_type.name}', active='{self.active}', "
            f"usage={[f'{usage.year}: {usage.amount:.2f}' for usage in self.usage]}')"
        )


class FertilizerUsage(Base):
    __tablename__ = "fertilizer_usage"
    __table_args__ = (UniqueConstraint("fertilizer_name", "year", name="unique_fertilizers"),)

    id = Column("id", Integer, primary_key=True)
    name = Column("fertilizer_name", String, ForeignKey("fertilizer.name"))
    year = Column("year", Integer)
    amount = Column("amount", Float(asdecimal=True))

    def __repr__(self):
        return (
            f"FertilizerUsage(name='{self.name}', year='{self.year}', amount='{self.amount:.2f}')"
        )


class SoilSample(Base):
    __tablename__ = "soil_sample"
    __table_args__ = (UniqueConstraint("base_id", "year", name="unique_samples"),)

    id = Column("sample_id", Integer, primary_key=True)
    base_id = Column("base_id", Integer, ForeignKey("base_field.base_id"))
    year = Column("year", Integer)
    ph = Column("ph", Float(asdecimal=True))
    p2o5 = Column("p2o5", Float(asdecimal=True))
    k2o = Column("k2o", Float(asdecimal=True))
    mg = Column("mg", Float(asdecimal=True))
    soil_type = Column("soil_type", Enum(SoilType))
    humus = Column("humus", Enum(HumusType))
    fields = relationship("Field", secondary=field_soil_sample, back_populates="soil_samples")

    def __repr__(self):
        return (
            f"SoilSample(id='{self.id}', year='{self.year}', "
            f"soil_type='{self.soil_type.value}', humus='{self.humus.value}', "
            f"fields={f'{[field.base_field.name for field in self.fields][0]}', [f'{field.year}' for field in self.fields]})"
        )


class Saldo(Base):
    __tablename__ = "saldo"

    field_id = Column("field_id", Integer, ForeignKey("field.field_id"), primary_key=True)
    n = Column("n", Float(asdecimal=True))
    p2o5 = Column("p2o5", Float(asdecimal=True))
    k2o = Column("k2o", Float(asdecimal=True))
    mgo = Column("mgo", Float(asdecimal=True))
    s = Column("s", Float(asdecimal=True))
    cao = Column("cao", Float(asdecimal=True))
    field = relationship("Field", back_populates="saldo")
