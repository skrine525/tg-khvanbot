import json
from sqlalchemy.orm.session import Session
from botsys.db.model import Database, KeyboardButton, User


# Проверяет наличие записи о пользователе в таблице. Если записи нет - создает ее.
def check_user(session: Session, user: User, tg_user_id: int) -> User:
    if user is None:
        user = User(tg_user_id)
        session.add(user)
        session.commit()

    return user


# Возвращает данные кнопки клавиатуры из таблицы БД
def get_keyboard_button_data(data_id: int, session: Session = None) -> dict:
    if session is None:
        session = Database.make_session()
        button_data = session.query(KeyboardButton).filter_by(id=data_id).first()
        session.close()
        if button_data is None:
            return {}
        else:
            return json.loads(button_data.data)
    else:
        button_data = session.query(KeyboardButton).filter_by(id=data_id).first()
        if button_data is None:
            return {}
        else:
            return json.loads(button_data.data)