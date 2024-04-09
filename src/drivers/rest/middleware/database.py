from typing import Any

from flask import Flask, g
from sqlalchemy.orm.session import Session, sessionmaker


class DatabaseMiddleware:
    def __init__(self, session_maker: sessionmaker[Session]):
        self.session_maker = session_maker

    def open(self) -> None:
        session = self.session_maker()
        g.session = session

    def close(self, *args: Any, **kwargs: Any) -> None:
        g.session.close()

    def register(self, app: Flask) -> None:
        app.before_request(self.open)
        app.teardown_request(self.close)
