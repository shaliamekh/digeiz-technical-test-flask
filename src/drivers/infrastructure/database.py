from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import sessionmaker


def create_session_maker(database_url: URL) -> sessionmaker[Session]:
    engine = create_engine(
        database_url,
        pool_size=15,
        max_overflow=15,
    )
    return sessionmaker(engine, autoflush=False, expire_on_commit=False)
