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
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import backref, relationship
from werkzeug.security import check_password_hash, generate_password_hash

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
from app.extensions import db

__all__ = [
    "BaseField",
    "Field",
    "Cultivation",
    "Crop",
    "Fertilization",
    "Fertilizer",
    "Modifier",
    "SoilSample",
    "Saldo",
    "User",
]

Base = db.Model
Column: Column = db.Column
Integer: Integer = db.Integer
String: String = db.String
relationship: relationship = db.relationship
ForeignKey: ForeignKey = db.ForeignKey
UniqueConstraint: UniqueConstraint = db.UniqueConstraint
Float: Float = db.Float
Boolean: Boolean = db.Boolean
Enum: Enum = db.Enum
backref: backref = db.backref


class User(UserMixin, Base):
    __tablename__ = "user"

    id = Column("user_id", Integer, primary_key=True)
    username = Column("username", String(64), index=True, unique=True)
    email = Column("email", String(120), index=True, unique=True)
    password_hash = Column("password_hash", String(128))
    year = Column("year", Integer)
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

    def get_crops(self, crop_class: CropClass = None, **kwargs):
        query = Crop.query.filter_by(user_id=self.id)
        if crop_class:
            query = query.filter_by(crop_class=crop_class)
        if kwargs:
            query = query.filter_by(**kwargs)
        return query.all()

    def get_fertilizers(self, fert_class: FertClass = None, **kwargs):
        query = Fertilizer.query.filter_by(user_id=self.id)
        if fert_class:
            query = query.filter_by(fert_class=fert_class)
        if kwargs:
            query = query.filter_by(**kwargs)
        return query.all()

    def __repr__(self):
        return f"<User {self.username}>"


class BaseField(Base):
    __tablename__ = "base_field"
    __table_args__ = (UniqueConstraint("user_id", "prefix", "suffix"),)

    user_id = Column("user_id", Integer, ForeignKey("user.user_id"))
    id = Column("base_id", Integer, primary_key=True)
    prefix = Column("prefix", Integer)
    suffix = Column("suffix", Integer)
    name = Column("name", String)

    fields = relationship("Field", back_populates="base_field", order_by="desc(Field.year)")
    soil_samples = relationship(
        "SoilSample", back_populates="base_field", order_by="desc(SoilSample.year)"
    )
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
    area = Column("area", Float(asdecimal=True, decimal_return_scale=2))
    year = Column("year", Integer)
    red_region = Column("red_region", Boolean)
    field_type = Column("field_type", Enum(FieldType))
    demand_p2o5 = Column("demand_p2o5", Enum(DemandType), server_default="demand")
    demand_k2o = Column("demand_k2o", Enum(DemandType), server_default="demand")
    demand_mgo = Column("demand_mgo", Enum(DemandType), server_default="demand")

    base_field = relationship("BaseField", back_populates="fields")
    cultivations = relationship("Cultivation", back_populates="field")
    fertilizations = relationship("Fertilization", back_populates="field")
    saldo = relationship("Saldo", back_populates="field", uselist=False)
    modifiers = relationship("Modifier", back_populates="field")

    @property
    def soil_samples(self):
        return self.base_field.soil_samples

    @property
    def fertilizers(self):
        return [fert.fertilizer for fert in self.fertilizations]

    def __repr__(self):
        return (
            f"Field(id='{self.id}', name='{self.base_field.prefix:02d}-{self.base_field.suffix} {self.base_field.name}', "
            f"year='{self.year}', ha='{self.area:.2f}', type='{self.field_type.value}', "
            f"soil_samples='{[sample.year for sample in self.soil_samples]}', "
            f"cultivations={[f'{cult.cultivation_type.value}: {cult.crop.name}' for cult in self.cultivations]}, "
            f"fertilizations={[f'{fert.cultivation.crop.name}: {fert.measure.value} -> {fert.fertilizer.name}' for fert in self.fertilizations]})"
        )


class Cultivation(Base):
    __tablename__ = "cultivation"
    __table_args__ = (UniqueConstraint("field_id", "cultivation_type"),)

    id = Column("cultivation_id", Integer, primary_key=True)
    field_id = Column("field_id", Integer, ForeignKey("field.field_id"))
    cultivation_type = Column("cultivation_type", Enum(CultivationType))
    crop_id = Column("crop_id", Integer, ForeignKey("crop.crop_id"))
    crop_yield = Column("yield", Integer)
    crop_protein = Column("protein", Float(asdecimal=True, decimal_return_scale=1))
    residues = Column("residues", Enum(ResidueType))
    legume_rate = Column("legume_rate", Enum(LegumeType))
    nmin_30 = Column("nmin_30", Integer)
    nmin_60 = Column("nmin_60", Integer)
    nmin_90 = Column("nmin_90", Integer)

    field = relationship("Field", back_populates="cultivations")
    crop = relationship("Crop", back_populates="cultivations")
    fertilizations = relationship("Fertilization", back_populates="cultivation")

    def __repr__(self):
        return (
            f"Cultivation(id='{self.id}', field='{self.field.base_field.name}', year='{self.field.year}', "
            f"type='{self.cultivation_type.value}', name='{self.crop.name}', yield='{self.crop_yield:.2f}', "
            f"residues='{self.residues.value}', legume='{self.legume_rate.value}', nmin='{self.nmin_30}, {self.nmin_60}, {self.nmin_90}')"
        )


class Crop(Base):
    __tablename__ = "crop"
    __table_args__ = (UniqueConstraint("user_id", "name"),)

    user_id = Column("user_id", Integer, ForeignKey("user.user_id"))
    id = Column("crop_id", Integer, primary_key=True)
    name = Column("name", String)
    field_type = Column("field_type", Enum(FieldType))
    crop_class = Column("class", Enum(CropClass))
    crop_type = Column("type", Enum(CropType))  # used for pre-crop effect
    kind = Column("kind", String)
    feedable = Column("feedable", Boolean)
    residue = Column("residue", Boolean)
    nmin_depth = Column("nmin_depth", Enum(NminType))
    target_demand = Column("target_demand", Integer)
    target_yield = Column("target_yield", Integer)
    pos_yield = Column("pos_yield", Float(asdecimal=True, decimal_return_scale=2))
    neg_yield = Column("neg_yield", Float(asdecimal=True, decimal_return_scale=2))
    target_protein = Column("target_protein", Float(asdecimal=True, decimal_return_scale=2))
    var_protein = Column("var_protein", Float(asdecimal=True, decimal_return_scale=2))
    p2o5 = Column("p2o5", Float(asdecimal=True, decimal_return_scale=2))
    k2o = Column("k2o", Float(asdecimal=True, decimal_return_scale=2))
    mgo = Column("mgo", Float(asdecimal=True, decimal_return_scale=2))
    byproduct = Column("byproduct", String)
    byp_ratio = Column("byp_ratio", Float(asdecimal=True, decimal_return_scale=2))
    byp_n = Column("byp_n", Float(asdecimal=True, decimal_return_scale=2))
    byp_p2o5 = Column("byp_p2o5", Float(asdecimal=True, decimal_return_scale=2))
    byp_k2o = Column("byp_k2o", Float(asdecimal=True, decimal_return_scale=2))
    byp_mgo = Column("byp_mgo", Float(asdecimal=True, decimal_return_scale=2))

    cultivations = relationship("Cultivation", back_populates="crop")

    def __repr__(self):
        return (
            f"Crop(id='{self.id}', name='{self.name}', type='{self.crop_type}', "
            f"var_yield='{self.pos_yield}, {self.neg_yield}')"
        )


class Fertilization(Base):
    __tablename__ = "fertilization"

    id = Column("fertilization_id", Integer, primary_key=True)
    field_id = Column("field_id", Integer, ForeignKey("field.field_id"))
    cultivation_id = Column("cultivation_id", Integer, ForeignKey("cultivation.cultivation_id"))
    fertilizer_id = Column("fertilizer_id", Integer, ForeignKey("fertilizer.fertilizer_id"))
    cut_timing = Column("cut_timing", Enum(CutTiming))
    amount = Column("amount", Float(asdecimal=True, decimal_return_scale=1))
    measure = Column("measure", Enum(MeasureType))
    month = Column("month", Integer)

    field = relationship("Field", back_populates="fertilizations")
    cultivation = relationship("Cultivation", back_populates="fertilizations")
    fertilizer = relationship("Fertilizer")

    def __repr__(self):
        return (
            f"Fertilization(id='{self.id}', name='{self.fertilizer.name}', amount='{self.amount:.1f}', "
            f"measure='{self.measure.value}', month='{self.month}', crop='{self.cultivation.crop.name}', "
            f"field='{self.field.base_field.name}')"
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
    price = Column("price", Float(asdecimal=True, decimal_return_scale=2))
    n = Column("n", Float(asdecimal=True, decimal_return_scale=2))
    p2o5 = Column("p2o5", Float(asdecimal=True, decimal_return_scale=2))
    k2o = Column("k2o", Float(asdecimal=True, decimal_return_scale=2))
    mgo = Column("mgo", Float(asdecimal=True, decimal_return_scale=2))
    s = Column("s", Float(asdecimal=True, decimal_return_scale=2))
    cao = Column("cao", Float(asdecimal=True, decimal_return_scale=2))
    nh4 = Column("nh4", Float(asdecimal=True, decimal_return_scale=2))

    def usage(self, year=None):
        """
        Summary of fertilizer consumption in a given year.

        :param year:
            Year which is summarized, mandatory for mineral fertilizers.
        :raises ValueError:
            Fails if no year is specified for mineral fertilizers.
        """
        if year is None:
            if not self.year:
                raise ValueError("Please specific a year.")
            year = self.year

        ferts = (
            Fertilization.query.join(Field)
            .join(Fertilizer)
            .filter(Field.year == year, Fertilizer.id == self.id)
            .all()
        )
        return sum(fert.amount * fert.field.area for fert in ferts)

    def __repr__(self):
        return (
            f"Fertilizer(id='{self.id}', name='{self.name}', year='{self.year}', "
            f"class='{self.fert_class.name}', type='{self.fert_type.name}', active='{self.active}')"
        )


class SoilSample(Base):
    __tablename__ = "soil_sample"
    __table_args__ = (UniqueConstraint("base_id", "year"),)

    id = Column("sample_id", Integer, primary_key=True)
    base_id = Column("base_id", Integer, ForeignKey("base_field.base_id"))
    year = Column("year", Integer)
    ph = Column("ph", Float(asdecimal=True, decimal_return_scale=2))
    p2o5 = Column("p2o5", Float(asdecimal=True, decimal_return_scale=2))
    k2o = Column("k2o", Float(asdecimal=True, decimal_return_scale=2))
    mg = Column("mg", Float(asdecimal=True, decimal_return_scale=2))
    soil_type = Column("soil_type", Enum(SoilType))
    humus = Column("humus", Enum(HumusType))

    base_field = relationship("BaseField", back_populates="soil_samples")

    @property
    def fields(self):
        return self.base_field.fields

    def __repr__(self):
        return (
            f"SoilSample(id='{self.id}', year='{self.year}', "
            f"soil_type='{self.soil_type.value}', humus='{self.humus.value}', "
            f"fields={f'{self.base_field.name}', [f'{field.year}' for field in self.fields if self.fields]})"
        )


class Modifier(Base):
    __tablename__ = "modifier"

    id = Column("modifier_id", Integer, primary_key=True)
    field_id = Column("field_id", Integer, ForeignKey("field.field_id"))
    description = Column("description", String)
    modification = Column("modification", Enum(NutrientType))
    amount = Column("amount", Integer)

    field = relationship("Field", back_populates="modifiers")


class Saldo(Base):
    __tablename__ = "saldo"

    field_id = Column("field_id", Integer, ForeignKey("field.field_id"), primary_key=True)
    n = Column("n", Float(asdecimal=True, decimal_return_scale=2))
    p2o5 = Column("p2o5", Float(asdecimal=True, decimal_return_scale=2))
    k2o = Column("k2o", Float(asdecimal=True, decimal_return_scale=2))
    mgo = Column("mgo", Float(asdecimal=True, decimal_return_scale=2))
    s = Column("s", Float(asdecimal=True, decimal_return_scale=2))
    cao = Column("cao", Float(asdecimal=True, decimal_return_scale=2))
    n_total = Column("nges", Float(asdecimal=True, decimal_return_scale=2))

    field = relationship("Field", back_populates="saldo")
