import logging
from typing import Any

import sqlalchemy as sa
from sqlalchemy.sql.expression import ColumnElement

from adapters.exceptions import (
    DatabaseException,
    MallNotFoundException,
    WallNotFoundException,
)
from adapters.repositories.models import WallORM
from domain.entities.mall import Mall
from domain.entities.wall import Wall
from ports.repositories.wall_repository import WallRepository

logger = logging.getLogger()


class SQLAlchemyWallRepository(WallRepository):
    def __init__(self, session: sa.orm.Session):
        self.session = session

    def add(self, wall: Wall) -> Wall:
        try:
            wall_orm = WallORM(id=wall.id, name=wall.name, mall_id=wall.mall_id)
            self.session.add(wall_orm)
            self.session.commit()
            return self._to_entity(wall_orm)
        except sa.exc.IntegrityError as e:
            logger.exception(e)
            self.session.rollback()
            if "wall_mall_id_fkey" in e.args[0]:
                raise MallNotFoundException({"id_filter": wall.mall_id})
            raise DatabaseException
        except sa.exc.SQLAlchemyError as e:
            logger.exception(e)
            self.session.rollback()
            raise DatabaseException

    def get(self, **filters: Any) -> Wall:
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = sa.select(WallORM).where(*filter_expressions)
            wall_orm = self.session.scalar(query)
            if not wall_orm:
                raise WallNotFoundException(filters)
            return self._to_entity(wall_orm)
        except sa.exc.SQLAlchemyError as e:
            logger.exception(e)
            raise DatabaseException

    def update(self, fields_to_update: dict[str, Any], **filters: Any) -> None:
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = (
                sa.update(WallORM).where(*filter_expressions).values(fields_to_update)
            )
            result = self.session.execute(query)
            self.session.commit()
            if not result.rowcount:
                raise WallNotFoundException(filters)
        except sa.exc.SQLAlchemyError as e:
            self.session.rollback()
            logger.error(e)
            raise DatabaseException

    def delete(self, **filters: Any) -> None:
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = sa.delete(WallORM).where(*filter_expressions)
            result = self.session.execute(query)
            self.session.commit()
            if not result.rowcount:
                raise MallNotFoundException(filters)
        except sa.exc.SQLAlchemyError as e:
            self.session.rollback()
            logger.error(e)
            raise DatabaseException

    def get_all(self, page: int = 1, limit: int = 50, **filters: Any) -> list[Wall]:
        offset = (page - 1) * limit
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = (
                sa.select(WallORM)
                .where(*filter_expressions)
                .offset(offset)
                .limit(limit)
            )
            result = self.session.scalars(query)
            return [self._to_entity(wall_orm) for wall_orm in result]
        except sa.exc.SQLAlchemyError as e:
            logger.exception(e)
            raise DatabaseException

    def count(self, **filters: Any) -> int:
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = (
                sa.select(sa.func.count())
                .select_from(WallORM)
                .where(*filter_expressions)
            )
            return self.session.scalar(query) or 0
        except sa.exc.SQLAlchemyError as e:
            logger.error(e)
            raise DatabaseException

    @staticmethod
    def _get_filter_expressions(filters: dict[str, Any]) -> list[ColumnElement[bool]]:
        filter_expressions = []
        if f := filters.get("id_filter"):
            filter_expressions.append(WallORM.id == f)
        if f := filters.get("name_filter"):
            filter_expressions.append(WallORM.name.like(f"%{f}%"))
        if f := filters.get("mall_id_filter"):
            filter_expressions.append(WallORM.mall_id == f)
        return filter_expressions

    @staticmethod
    def _to_entity(wall_orm: WallORM) -> Wall:
        return Wall(
            id=wall_orm.id,
            name=wall_orm.name,
            mall_id=wall_orm.mall_id,
            mall=Mall(id=wall_orm.mall.id, name=wall_orm.mall.name),
        )
