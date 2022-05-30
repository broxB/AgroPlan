from decimal import Decimal, getcontext

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

Base = declarative_base()

field_cultivation = Table(
    "field_cultivation",
    Base.metadata,
    Column("field_id", Integer, ForeignKey("field.field_id")),
    Column("cultivation_id", Integer, ForeignKey("cultivation.cultivation_id")),
)

cultivation_fertilization = Table(
    "cultivation_fertilization",
    Base.metadata,
    Column("cultivation_id", Integer, ForeignKey("cultivation.cultivation_id")),
    Column("fertilization_id", Integer, ForeignKey("fertilization.fertilization_id")),
)


class Field(Base):
    __tablename__ = "field"
    id = Column("field_id", Integer, primary_key=True)
    prefix = Column("prefix", Integer)
    suffix = Column("suffix", Integer)
    name = Column("name", String)
    area = Column("area", Float(asdecimal=True))
    type = Column("type", String)
    # cultivations = relationship(
    #     "Cultivation", secondary=field_cultivation, back_populates="field"
    # )

    def __repr__(self):
        return f"Field(id='{self.id}', name='{self.prefix}-{self.suffix} {self.name}', ha='{self.area:.2f}')"


class Cultivation(Base):
    __tablename__ = "cultivation"
    id = Column("cultivation_id", Integer, primary_key=True)
    year = Column("year", Integer)
    field_id = Column("field_id", Integer, ForeignKey("field.field_id"))
    crops = relationship("CultivatedCrop", backref=backref("cultivation"))
    fertilizations = relationship(
        "Fertilization",
        secondary=cultivation_fertilization,
        back_populates="cultivations",
    )
    field = relationship("Field", backref=backref("cultivation"))
    __table_args__ = (
        UniqueConstraint(
            "cultivation_id", "field_id", "year", name="active_cultivations"
        ),
    )

    def __repr__(self):
        return f"Cultivation(id='{self.id}', year='{self.year}', field='{self.field.name}')"


class CultivatedCrop(Base):
    __tablename__ = "cultivated_crop"
    id = Column("cultivated_crop_id", Integer, primary_key=True)
    cultivation_id = Column(
        "cultivation_id", Integer, ForeignKey("cultivation.cultivation_id")
    )
    crop_type = Column("crop_type", String)
    crop_id = Column("crop_id", Integer, ForeignKey("crop.crop_id"))
    crop_yield = Column("yield", Float(asdecimal=True))
    remains = Column("remains", Boolean)
    legume_rate = Column("legume_rate", String)
    crops = relationship("Crop", backref=backref("cultivated_crop"))

    def __repr__(self):
        return f"CultivatedCrop(id='{self.id}', type='{self.crop_type}', name='{self.crops.name}')"


class Crop(Base):
    __tablename__ = "crop"
    id = Column("crop_id", Integer, primary_key=True)
    name = Column("name", String, unique=True)

    def __repr__(self):
        return f"Crop(id='{self.id}', name='{self.name}')"


class Fertilization(Base):
    __tablename__ = "fertilization"
    id = Column("fertilization_id", Integer, primary_key=True)
    cultivated_crop_id = Column(
        "cultivated_crop_id", Integer, ForeignKey("cultivated_crop.cultivated_crop_id")
    )
    fertilizer_id = Column(
        "fertilizer_id", Integer, ForeignKey("fertilizer.fertilizer_id")
    )
    amount = Column("amount", Float(asdecimal=True))
    measure = Column("measure", String)
    month = Column("month", Integer)
    cultivations = relationship(
        "Cultivation",
        secondary=cultivation_fertilization,
        back_populates="fertilizations",
    )
    name = relationship("Fertilizer", backref=backref("fertilization"))

    def __repr__(self):
        return f"Fertilization(id='{self.id}', name='{self.name.name}', amount='{self.amount:.2f}', measure='{self.measure}', month='{self.month}')"


class Fertilizer(Base):
    __tablename__ = "fertilizer"
    id = Column("fertilizer_id", Integer, primary_key=True)
    name = Column("name", String, unique=True)
    year = Column("year", Integer)
    type = Column("type", String)
    active = Column("active", Boolean, nullable=True)

    def __repr__(self):
        return f"Fertilizer(id='{self.id}', name='{self.name}', year='{self.year}', type='{self.type}', active='{self.active}')"
