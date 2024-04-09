from typing import Type

from flask import Flask
from flask_apispec.extension import FlaskApiSpec
from flask_restful import Api

from drivers.infrastructure.database import create_session_maker
from drivers.rest.config import BaseConfig, get_config_cls
from drivers.rest.controllers.footfalls import (
    FootfallController,
    FootfallItemController,
)
from drivers.rest.controllers.footfalls_import_data import FootfallImportDataController
from drivers.rest.controllers.healthcheck import HealthCheck
from drivers.rest.controllers.malls import MallController, MallItemController
from drivers.rest.controllers.walls import WallController, WallItemController
from drivers.rest.error_handlers import handle_errors
from drivers.rest.middleware.database import DatabaseMiddleware
from logger import configure_logging


def create_app(config_cls: Type[BaseConfig] | None = None) -> Flask:
    app = Flask(__name__)

    if config_cls is None:
        config_cls = get_config_cls()
    app.config.from_object(config_cls)

    session_maker = create_session_maker(config_cls().database_url)
    DatabaseMiddleware(session_maker).register(app)

    api = Api(app)

    configure_logging(config_cls())

    handle_errors(app)

    path_prefix = app.config["PATH_PREFIX"]
    api.add_resource(HealthCheck, "/healthcheck")
    api.add_resource(MallController, f"{path_prefix}/malls")
    api.add_resource(MallItemController, f"{path_prefix}/malls/<string:mall_id>")
    api.add_resource(WallController, f"{path_prefix}/walls")
    api.add_resource(WallItemController, f"{path_prefix}/walls/<string:wall_id>")
    api.add_resource(FootfallController, f"{path_prefix}/footfalls")
    api.add_resource(
        FootfallItemController, f"{path_prefix}/footfalls/<string:footfall_id>"
    )
    api.add_resource(
        FootfallImportDataController, f"{path_prefix}/footfalls/import-data"
    )

    docs = FlaskApiSpec(app)
    docs.register(MallController)
    docs.register(MallItemController)
    docs.register(WallController)
    docs.register(WallItemController)
    docs.register(FootfallController)
    docs.register(FootfallItemController)
    docs.register(FootfallImportDataController)

    return app
