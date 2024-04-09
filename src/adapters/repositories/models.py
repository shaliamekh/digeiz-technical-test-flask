from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from domain.entities.footfall import OriginType


class Base(DeclarativeBase):
    type_annotation_map = {datetime: sa.DateTime()}


class MallORM(Base):
    __tablename__ = "mall"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]


class WallORM(Base):
    __tablename__ = "wall"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    mall_id: Mapped[int] = mapped_column(sa.ForeignKey("mall.id", ondelete="CASCADE"))
    mall: Mapped["MallORM"] = relationship(lazy="joined")


class FootfallORM(Base):
    __tablename__ = "footfall"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    start_datetime: Mapped[datetime]
    end_datetime: Mapped[datetime]
    people_in: Mapped[int]
    people_out: Mapped[int]
    is_active: Mapped[bool]
    origin: Mapped[OriginType]
    wall_id: Mapped[int] = mapped_column(sa.ForeignKey("wall.id", ondelete="CASCADE"))
    wall: Mapped["WallORM"] = relationship(lazy="joined")
