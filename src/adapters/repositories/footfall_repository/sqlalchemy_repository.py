import logging
from typing import Any

import sqlalchemy as sa
from sqlalchemy.sql.expression import ColumnElement

from adapters.exceptions import (
    DatabaseException,
    FootfallNotFoundException,
    WallNotFoundException,
)
from adapters.repositories.models import FootfallORM
from domain.entities.footfall import Footfall
from domain.entities.mall import Mall
from domain.entities.wall import Wall
from ports.repositories.footfall_repository import FootfallRepository

logger = logging.getLogger()


class SQLAlchemyFootfallRepository(FootfallRepository):
    def __init__(self, session: sa.orm.Session):
        self.session = session

    def add(self, footfall: Footfall) -> Footfall:
        try:
            footfall_orm = self._to_orm(footfall)
            self.session.add(footfall_orm)
            self.session.commit()
            return self._to_entity(footfall_orm)
        except sa.exc.IntegrityError as e:
            logger.exception(e)
            self.session.rollback()
            if "footfall_wall_id_fkey" in e.args[0]:
                raise WallNotFoundException({"id_filter": footfall.wall_id})
            raise DatabaseException
        except sa.exc.SQLAlchemyError as e:
            logger.exception(e)
            self.session.rollback()
            raise DatabaseException

    def get(self, **filters: Any) -> Footfall:
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = sa.select(FootfallORM).where(*filter_expressions)
            footfall_orm = self.session.scalar(query)
            if not footfall_orm:
                raise FootfallNotFoundException(filters)
            return self._to_entity(footfall_orm)
        except sa.exc.SQLAlchemyError as e:
            logger.exception(e)
            raise DatabaseException

    def update(
        self, fields_to_update: dict[str, Any], with_error: bool = True, **filters: Any
    ) -> None:
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = (
                sa.update(FootfallORM)
                .where(*filter_expressions)
                .values(fields_to_update)
            )
            result = self.session.execute(query)
            self.session.commit()
            if not result.rowcount and with_error:
                raise FootfallNotFoundException(filters)
        except sa.exc.SQLAlchemyError as e:
            self.session.rollback()
            logger.error(e)
            raise DatabaseException

    def delete(self, **filters: Any) -> None:
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = sa.delete(FootfallORM).where(*filter_expressions)
            result = self.session.execute(query)
            self.session.commit()
            if not result.rowcount:
                raise FootfallNotFoundException(filters)
        except sa.exc.SQLAlchemyError as e:
            self.session.rollback()
            logger.error(e)
            raise DatabaseException

    def get_all(self, page: int = 1, limit: int = 50, **filters: Any) -> list[Footfall]:
        offset = (page - 1) * limit
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = (
                sa.select(FootfallORM)
                .where(*filter_expressions)
                .offset(offset)
                .limit(limit)
            )
            result = self.session.scalars(query)
            return [self._to_entity(footfall_orm) for footfall_orm in result]
        except sa.exc.SQLAlchemyError as e:
            logger.exception(e)
            raise DatabaseException

    def count(self, **filters: Any) -> int:
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = (
                sa.select(sa.func.count())
                .select_from(FootfallORM)
                .where(*filter_expressions)
            )
            return self.session.scalar(query) or 0
        except sa.exc.SQLAlchemyError as e:
            logger.error(e)
            raise DatabaseException

    def add_batch(self, footfalls: list[Footfall]) -> None:
        try:
            self.session.add_all([self._to_orm(footfall) for footfall in footfalls])
            self.session.commit()
        except sa.exc.IntegrityError as e:
            logger.exception(e)
            self.session.rollback()
            if "footfall_wall_id_fkey" in e.args[0]:
                raise WallNotFoundException({"id_filter": "batch_add"})
            raise DatabaseException
        except sa.exc.SQLAlchemyError as e:
            logger.exception(e)
            self.session.rollback()
            raise DatabaseException

    @staticmethod
    def _get_filter_expressions(filters: dict[str, Any]) -> list[ColumnElement[bool]]:
        filter_expressions = []
        if f := filters.get("id_filter"):
            filter_expressions.append(FootfallORM.id == f)
        if f := filters.get("wall_id_filter"):
            filter_expressions.append(FootfallORM.wall_id == f)
        if (f := filters.get("is_active_filter")) is not None:
            filter_expressions.append(FootfallORM.is_active == f)
        if f := filters.get("origin_filter"):
            filter_expressions.append(FootfallORM.origin == f)
        if f := filters.get("start_date_between_filter"):
            condition = sa.and_(
                FootfallORM.start_datetime >= f[0],
                FootfallORM.start_datetime <= f[1],
            )
            filter_expressions.append(condition)
        return filter_expressions

    @staticmethod
    def _to_entity(footfall_orm: FootfallORM) -> Footfall:
        wall = Wall(
            id=footfall_orm.wall.id,
            name=footfall_orm.wall.name,
            mall_id=footfall_orm.wall.mall_id,
            mall=Mall(id=footfall_orm.wall.mall.id, name=footfall_orm.wall.mall.name),
        )
        return Footfall(
            id=footfall_orm.id,
            start_datetime=footfall_orm.start_datetime,
            end_datetime=footfall_orm.end_datetime,
            people_in=footfall_orm.people_in,
            people_out=footfall_orm.people_out,
            is_active=footfall_orm.is_active,
            origin=footfall_orm.origin,
            wall_id=footfall_orm.wall_id,
            wall=wall,
        )

    @staticmethod
    def _to_orm(footfall: Footfall) -> FootfallORM:
        return FootfallORM(
            id=footfall.id,
            start_datetime=footfall.start_datetime,
            end_datetime=footfall.end_datetime,
            people_in=footfall.people_in,
            people_out=footfall.people_out,
            is_active=footfall.is_active,
            origin=footfall.origin,
            wall_id=footfall.wall_id,
        )
