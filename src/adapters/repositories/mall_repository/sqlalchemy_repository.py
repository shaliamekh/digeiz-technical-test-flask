import logging
from typing import Any

import sqlalchemy as sa
from sqlalchemy.sql.expression import ColumnElement

from adapters.exceptions import DatabaseException, MallNotFoundException
from adapters.repositories.models import MallORM
from domain.entities.mall import Mall
from ports.repositories.mall_repository import MallRepository

logger = logging.getLogger()


class SQLAlchemyMallRepository(MallRepository):
    def __init__(self, session: sa.orm.Session):
        self.session = session

    def add(self, mall: Mall) -> Mall:
        try:
            mall_orm = MallORM(id=mall.id, name=mall.name)
            self.session.add(mall_orm)
            self.session.commit()
            return Mall(id=mall_orm.id, name=mall_orm.name)
        except sa.exc.SQLAlchemyError as e:
            logger.exception(e)
            self.session.rollback()
            raise DatabaseException

    def get(self, **filters: Any) -> Mall:
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = sa.select(MallORM).where(*filter_expressions)
            mall_orm = self.session.scalar(query)
            if not mall_orm:
                raise MallNotFoundException(filters)
            return Mall(id=mall_orm.id, name=mall_orm.name)
        except sa.exc.SQLAlchemyError as e:
            logger.exception(e)
            raise DatabaseException

    def update(self, fields_to_update: dict[str, Any], **filters: Any) -> None:
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = (
                sa.update(MallORM).where(*filter_expressions).values(fields_to_update)
            )
            result = self.session.execute(query)
            self.session.commit()
            if not result.rowcount:
                raise MallNotFoundException(filters)
        except sa.exc.SQLAlchemyError as e:
            self.session.rollback()
            logger.error(e)
            raise DatabaseException

    def delete(self, **filters: Any) -> None:
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = sa.delete(MallORM).where(*filter_expressions)
            result = self.session.execute(query)
            self.session.commit()
            if not result.rowcount:
                raise MallNotFoundException(filters)
        except sa.exc.SQLAlchemyError as e:
            self.session.rollback()
            logger.error(e)
            raise DatabaseException

    def get_all(self, page: int = 1, limit: int = 50, **filters: Any) -> list[Mall]:
        offset = (page - 1) * limit
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = (
                sa.select(MallORM)
                .where(*filter_expressions)
                .offset(offset)
                .limit(limit)
            )
            result = self.session.scalars(query)
            return [Mall(id=mall_orm.id, name=mall_orm.name) for mall_orm in result]
        except sa.exc.SQLAlchemyError as e:
            logger.exception(e)
            raise DatabaseException

    def count(self, **filters: Any) -> int:
        filter_expressions = self._get_filter_expressions(filters)
        try:
            query = (
                sa.select(sa.func.count())
                .select_from(MallORM)
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
            filter_expressions.append(MallORM.id == f)
        if f := filters.get("name_filter"):
            filter_expressions.append(MallORM.name.like(f"%{f}%"))
        return filter_expressions
