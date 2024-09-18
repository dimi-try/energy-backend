from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Numeric, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional

Base = declarative_base()

class BrandOrm(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

class EnergeticOrm(Base):
    __tablename__ = "energetics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"))
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    ingredients: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String(255))
    price_category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("price_categories.id"))

class RatingOrm(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    energy_id: Mapped[int] = mapped_column(ForeignKey("energetics.id"))
    rating: Mapped[Optional[Numeric]] = mapped_column(Numeric(20, 10))
    review: Mapped[Optional[str]] = mapped_column(Text)
    criteria_id: Mapped[Optional[int]] = mapped_column(ForeignKey("criteria.id"))
    created_at: Mapped[Optional[str]] = mapped_column(TIMESTAMP, nullable=False)
    is_history: Mapped[bool] = mapped_column(Boolean, default=False)
    original_rating_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ratings.id"))
