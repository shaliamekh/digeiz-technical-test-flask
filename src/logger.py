import logging

from drivers.rest.config import BaseConfig


def configure_logging(config: BaseConfig) -> None:
    logging_level = logging.DEBUG if config.DEBUG else logging.INFO
    logging.basicConfig(level=logging_level)
