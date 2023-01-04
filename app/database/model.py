from time import time

from flask import current_app
from flask_login import UserMixin
from jwt import InvalidSignatureError, decode, encode
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
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import backref, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.database.base import Model as Base
from app.database.types import (
    CropClass,
    CropType,
    DemandType,
    FertClass,
    FertType,
    FieldType,
    HumusType,
    LegumeType,
    MeasureType,
    ResidueType,
    SoilType,
    UnitType,
)

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
    "Saldo",
    "User",
]


class User(UserMixin, Base):
    __tablename__ = "user"

    id = Column("user_id", Integer, primary_key=True)
    username = Column("username", String(64), index=True, unique=True)
    email = Column("email", String(120), index=True, unique=True)
    password_hash = Column("password_hash", String(128))
    year = Column("set_year", Integer)
    fields = relationship("BaseField", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])[
                "reset_password"
            ]
        except InvalidSignatureError:
            return None
        return User.query.get(user_id)

    def get_fields(self, year: int = None):
        if year is None:
            return BaseField.query.filter(BaseField.user_id == self.id)
        return BaseField.query.join(Field).filter(BaseField.user_id == self.id, Field.year == year)

    def get_years(self):
        fields = (
            Field.query.join(BaseField).filter(BaseField.user_id == self.id).group_by(Field.year)
        )
        return [field.year for field in fields]

    def __repr__(self):
        return f"<User {self.username}>"


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
    __table_args__ = (UniqueConstraint("user_id", "prefix", "suffix"),)

    user_id = Column("user_id", Integer, ForeignKey("user.user_id"))
    id = Column("base_id", Integer, primary_key=True)
    prefix = Column("prefix", Integer)
    suffix = Column("suffix", Integer)
    name = Column("name", String)
    fields = relationship("Field", back_populates="base_field", order_by="desc(Field.year)")
    soil_samples = relationship("SoilSample")
    user = relationship("User", back_populates="fields")

    def __repr__(self):
        return (
            f"BaseField(id='{self.id}', name='{self.prefix:02d}-{self.suffix} {self.name}', "
            f"fields='{[f'{field.year}: {field.field_type.value}, {field.area:.2f}ha' for field in self.fields]}'"
        )


class Field(Base):
    __tablename__ = "field"
    __table_args__ = (UniqueConstraint("base_id", "sub_suffix", "year"),)

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
    __table_args__ = (UniqueConstraint("field_id", "crop_class"),)

    id = Column("cultivation_id", Integer, primary_key=True)
    field_id = Column("field_id", Integer, ForeignKey("field.field_id"))
    crop_class = Column("crop_class", Enum(CropClass))
    crop_id = Column("crop_id", Integer, ForeignKey("crop.crop_id"))
    crop_yield = Column("yield", Float(asdecimal=True))
    crop_protein = Column("protein", Float(asdecimal=True))
    residues = Column("residues", Enum(ResidueType))
    legume_rate = Column("legume_rate", Enum(LegumeType))
    nmin = Column("nmin", MutableList.as_mutable(PickleType), default=[])
    field = relationship("Field", back_populates="cultivations")
    crop = relationship("Crop", back_populates="cultivations")

    def __repr__(self):
        return (
            f"Cultivation(id='{self.id}', field='{self.field.base_field.name}', year='{self.field.year}', "
            f"type='{self.crop_class.value}', name='{self.crop.name}', yield='{self.crop_yield:.2f}', "
            f"residues='{self.residues.value}', legume='{self.legume_rate.value}', nmin='{self.nmin}')"
        )


class Crop(Base):
    __tablename__ = "crop"
    __table_args__ = (UniqueConstraint("user_id", "name"),)

    user_id = Column("user_id", Integer, ForeignKey("user.user_id"))
    id = Column("crop_id", Integer, primary_key=True)
    name = Column("name", String)
    crop_class = Column("class", Enum(CropClass))
    crop_type = Column("type", Enum(CropType))  # used for pre-crop effect
    kind = Column("kind", String)
    feedable = Column("feedable", Boolean)
    residue = Column("residue", Boolean)
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
    __table_args__ = (UniqueConstraint("user_id", "name", "year"),)

    user_id = Column("user_id", Integer, ForeignKey("user.user_id"))
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
    __table_args__ = (UniqueConstraint("user_id", "fertilizer_name", "year"),)

    user_id = Column("user_id", Integer, ForeignKey("user.user_id"))
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
    __table_args__ = (UniqueConstraint("base_id", "year"),)

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
    n_total = Column("nges", Float(asdecimal=True))
    field = relationship("Field", back_populates="saldo")
