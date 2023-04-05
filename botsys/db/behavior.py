from sqlalchemy.orm.session import Session
from botsys.db.model import  User


# Проверяет наличие записи о пользователе в таблице. Если записи нет - создает ее.
def check_user(session: Session, user: User, tg_user_id: int) -> User:
    if user is None:
        user = User(tg_user_id)
        session.add(user)
        session.commit()

    return user
