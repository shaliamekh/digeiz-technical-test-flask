import os
from enum import StrEnum
from typing import Type

import sqlalchemy as sa
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin


class EnvType(StrEnum):
    LOCAL = "local"
    TEST = "test"


class BaseConfig:
    ENV = os.environ.get("API_ENVIRONMENT", EnvType.LOCAL)
    DEBUG = False
    TESTING = False
    PATH_PREFIX = "/api"
    APISPEC_SPEC = APISpec(
        title="Digeiz Service",
        version="v1",
        plugins=[MarshmallowPlugin()],
        openapi_version="2.0.0",
    )
    APISPEC_SWAGGER_URL = "/openapi-json"
    APISPEC_SWAGGER_UI_URL = "/docs"
    DB_HOST = os.environ.get("DB_HOST")
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_NAME = os.environ.get("DB_NAME")

    @property
    def database_url(self) -> sa.URL:
        return sa.URL.create(
            drivername="postgresql",
            host=self.DB_HOST,
            username=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            database=self.DB_NAME,
        )


class LocalConfig(BaseConfig):
    DEBUG = True
    DB_HOST = "digeiz-postgres"
    DB_USERNAME = "digeiz"
    DB_PASSWORD = "digeiz"
    DB_NAME = "digeiz"


class TestingConfig(BaseConfig):
    TESTING = True
    DB_HOST = "digeiz-postgres"
    DB_USERNAME = "digeiz"
    DB_PASSWORD = "digeiz"
    DB_NAME = "digeiz"


environments = {EnvType.LOCAL: LocalConfig, EnvType.TEST: TestingConfig}


def get_config_cls() -> Type[BaseConfig]:
    env = os.getenv("API_ENVIRONMENT", EnvType.LOCAL)
    return environments[env]  # type: ignore
