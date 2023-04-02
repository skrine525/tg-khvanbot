from sqlalchemy import Column, ForeignKey, SmallInteger, Integer, BigInteger, String, Boolean, JSON, VARCHAR, UUID, TIMESTAMP, create_engine
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm.session import Session
from sqlalchemy.engine import Engine
import datetime


# Статический класс для доступа к движку БД
class Database:
    engine: Engine

    Base = declarative_base()

    @staticmethod
    def create_engine(url: str):
        Database.engine = create_engine(url)

    @staticmethod
    def make_session() -> Session:
        return Session(bind=Database.engine)


# Системная таблица для хранения данных внутри callback кнопок
class KeyboardButton(Database.Base):
    __tablename__ = 'system_keyboard_buttons'

    # Столбцы
    id = Column(UUID, primary_key=True)
    data = Column(JSON, nullable=False)

    # Конструктор
    def __init__(self, data: str):
        self.data = data

    # Преобразование в строку
    def __repr__(self):
        return f"<KeyboardButton('{self.id}')>"


# Пользователь
class User(Database.Base):
    __tablename__ = 'users'

    # Столбцы
    id = Column(BigInteger, primary_key=True)                               # Числовой идентификатор
    tg_user_id = Column(BigInteger, unique=True)                            # Идентификатор аккаунта Telegram
    first_name = Column(VARCHAR(20), default="")                            # Имя пользователя
    last_name = Column(VARCHAR(20), default="")                             # Фамилия пользователя
    middle_name = Column(VARCHAR(20), default="")                           # Отчество пользователя
    is_deactivated = Column(Boolean, nullable=False, default=False)         # Статус деактивации аккаунта

    # Отношения
    role = relationship('UserRole', backref='user', uselist=False)

    # Конструктор
    def __init__(self, tg_user_id: int):
        self.tg_user_id = tg_user_id

    # Преобразование в строку
    def __repr__(self):
        return f"<User({self.id}, {self.tg_user_id})>"
    

# Специальные роли
class UserRole(Database.Base):
    __tablename__ = 'user_roles'

    # Константы
    ROLE_MANAGER = 'm'
    ROLE_TEACHER = 't'
    ROLE_ADMIN = 'a'

    # Столбцы
    id = Column(BigInteger, primary_key=True)                               # Числовой идентификатор
    user_id = Column(BigInteger, ForeignKey("users.id"), unique=True)       # Идентификатор пользователя
    role = Column(VARCHAR(1), nullable=False)                               # Роль пользователя
    timestamp = Column(TIMESTAMP, default=datetime.datetime.utcnow)         # Временная метка назначения роли

    # Конструктор
    def __init__(self, user_id: int, role: str):
        self.user_id = user_id
        self.role = role

    # Преобразование в строку
    def __repr__(self):
        return f"<UserRole({self.id}, {self.user_id}, '{self.role}')>"
    
    # Проверка пользователя на роль Менеджер
    def is_manager(self):
        return (self.role == UserRole.ROLE_MANAGER)
    
    # Проверка пользователя на роль Учитель
    def is_teacher(self):
        return (self.role == UserRole.ROLE_TEACHER)
    
    # Проверка пользователя на роль Администратор
    def is_admin(self):
        return (self.role == UserRole.ROLE_ADMIN)
