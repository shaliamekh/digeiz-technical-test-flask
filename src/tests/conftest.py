import pytest
import sqlalchemy as sa
from flask import Flask
from sqlalchemy.orm import sessionmaker

from adapters.repositories.footfall_repository.sqlalchemy_repository import (
    SQLAlchemyFootfallRepository,
)
from adapters.repositories.mall_repository.sqlalchemy_repository import (
    SQLAlchemyMallRepository,
)
from adapters.repositories.models import Base, FootfallORM, MallORM, WallORM
from adapters.repositories.wall_repository.sqlalchemy_repository import (
    SQLAlchemyWallRepository,
)
from drivers.rest.config import TestingConfig
from drivers.rest.main import create_app


@pytest.fixture(scope="session")
def engine():
    database_url = TestingConfig().database_url
    return sa.create_engine(database_url)


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    session_maker = sessionmaker(
        bind=engine, expire_on_commit=False, autoflush=False, autocommit=False
    )
    with session_maker() as session:
        yield session


@pytest.fixture
def mall_repository(db_session):
    return SQLAlchemyMallRepository(db_session)


@pytest.fixture
def wall_repository(db_session):
    return SQLAlchemyWallRepository(db_session)


@pytest.fixture
def footfall_repository(db_session):
    return SQLAlchemyFootfallRepository(db_session)


@pytest.fixture(autouse=True)
def truncate_tables(db_session):
    for table in (WallORM, MallORM, FootfallORM):
        db_session.execute(sa.delete(table))


@pytest.fixture(scope="session")
def app():
    return create_app(TestingConfig)


@pytest.fixture(scope="session")
def client(app: Flask):
    return app.test_client()
