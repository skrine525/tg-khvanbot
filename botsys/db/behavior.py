from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session
from sqlalchemy.engine import Engine
from botsys.db.model import User


# Класс для доступа к движку БД
class Database:
    engine: Engine

    @staticmethod
    def create_engine(url: str):
        Database.engine = create_engine(url)

    @staticmethod
    def make_session() -> Session:
        return Session(bind=Database.engine)
