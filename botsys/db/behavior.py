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

# Проверяет наличие записи о пользователе в таблице. Если записи нет - создает ее.
def check_user(session: Session, user: User, tg_user_id: int) -> User:
    if user is None:
        user = User(tg_user_id)
        session.add(user)
        session.commit()

    return user
