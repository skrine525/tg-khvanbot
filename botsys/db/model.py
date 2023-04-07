from sqlalchemy import Column, ForeignKey, SmallInteger, Integer, BigInteger, String, Boolean, JSON, VARCHAR, UUID, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship
import datetime, uuid


Base = declarative_base() # Базовый класс модели

# Системная таблица для хранения данных внутри callback кнопок
class KeyboardButton(Base):
    __tablename__ = 'system_keyboard_buttons'

    # Столбцы
    button_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    data = Column(JSON, nullable=False)
    keyboard_token = Column(VARCHAR(32), nullable=False)

    # Конструктор
    def __init__(self, data: dict, keyboard_token: str):
        self.data = data
        self.keyboard_token = keyboard_token

    # Преобразование в строку
    def __repr__(self):
        return f"<KeyboardButton('{self.button_id}')>"


# Пользователь
class User(Base):
    __tablename__ = 'users'

    # Столбцы
    user_id = Column(BigInteger, primary_key=True)                                          # Числовой идентификатор
    tg_user_id = Column(BigInteger, unique=True)                                            # Идентификатор аккаунта Telegram
    first_name = Column(VARCHAR(20), nullable=False)                                        # Имя пользователя
    last_name = Column(VARCHAR(20), default=None)                                           # Фамилия пользователя
    middle_name = Column(VARCHAR(20), default=None)                                         # Отчество пользователя
    register_time = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)     # Время регистрации пользователя
    tz_msc_offset = Column(SmallInteger, nullable=False, default=0)                         # Часовой пояс относительно Московского времени
    is_deactivated = Column(Boolean, nullable=False, default=False)                         # Статус деактивации аккаунта

    # Отношения
    role = relationship('UserRole', backref='user', uselist=False, cascade="all,delete")
    consultations = relationship('Сonsultation', backref='user', uselist=True, cascade="all,delete", lazy="dynamic")

    # Конструктор
    def __init__(self, tg_user_id: int):
        self.tg_user_id = tg_user_id

    # Преобразование в строку
    def __repr__(self):
        return f"<User({self.user_id}, {self.tg_user_id})>"
    
    # Возвращает полное имя пользователя
    def get_full_name(self, last_name=True, middle_name=True):
        full_name = self.first_name
        if last_name and self.last_name is not None:
            full_name = f"{self.last_name} {full_name}"
        if middle_name and self.middle_name is not None:
            full_name = f"{full_name} {self.middle_name}"
        return full_name
    

# Специальные роли
class UserRole(Base):
    __tablename__ = 'user_roles'

    # Константы
    ROLE_TEACHER = 't'
    ROLE_ADMIN = 'a'

    # Столбцы
    user_role_id = Column(BigInteger, primary_key=True)                                     # Идентификатор роли пользователя
    user_id = Column(BigInteger, ForeignKey("users.user_id"), unique=True)                  # Идентификатор пользователя
    role = Column(VARCHAR(1), nullable=False)                                               # Роль пользователя
    acquisition_time = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)  # Временная метка получения роли

    # Конструктор
    def __init__(self, user_id: int, role: str):
        self.user_id = user_id
        self.role = role

    # Преобразование в строку
    def __repr__(self):
        return f"<UserRole({self.user_role_id}, {self.user_id}, '{self.role}')>"
    
    # Проверка пользователя на роль Учитель
    def is_teacher(self):
        return (self.role == UserRole.ROLE_TEACHER)
    
    # Проверка пользователя на роль Администратор
    def is_admin(self):
        return (self.role == UserRole.ROLE_ADMIN)


# Записи на консультацию
class Сonsultation(Base):
    __tablename__ = 'consultations'

    # Столбцы
    consultation_id = Column(BigInteger, primary_key=True)                                  # Идентификатор консультации
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)               # Идентификатор пользователя
    creation_time = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)     # Время создания записи на консультацию
    is_processed = Column(Boolean, nullable=False, default=False)                           # Статус консультации
    phone_number = Column(VARCHAR(20), nullable=False)                               # Ответ на вопрос "Номер телефона"
    lang_level = Column(VARCHAR(50), nullable=False)                                 # Ответ на вопрос "Уровень языка"
    hsk_exam = Column(VARCHAR(100), nullable=False)                                  # Ответ на вопрос "Экзамен HSK"
    purpose = Column(VARCHAR(100), nullable=False)                                   # Ответ на вопрос "Цель изучения"
    way_now = Column(VARCHAR(50), nullable=False)                                    # Ответ на вопрос "Способ изучения сейчас"
    consultation_time = Column(TIMESTAMP, nullable=False)                                   # Удобное время консультации

    # Конструктор
    def __init__(self, user_id: int, phone_number:str, lang_level: str, hsk_exam: str, purpose: str, way_now: str, consultation_time: datetime.datetime):
        self.user_id = user_id
        self.phone_number = phone_number
        self.lang_level = lang_level
        self.hsk_exam = hsk_exam
        self.purpose = purpose
        self.way_now = way_now
        self.consultation_time = consultation_time

    # Преобразование в строку
    def __repr__(self):
        return f"<Сonsultation({self.consultation_id}, {self.user_id})>"
    
# Таблица списка времён, которые доступны во время записи на консультацию
class СonsultationTime(Base):
    __tablename__ = 'consultation_times'

    # Столбцы
    consultation_time_id = Column(BigInteger, primary_key=True)
    utc_hour = Column(SmallInteger, nullable=False)
    utc_minute = Column(SmallInteger, nullable=False)

    # Конструктор
    def __init__(self, utc_hour: int, utc_minute: int):
        self.utc_hour = utc_hour
        self.utc_minute = utc_minute

    # Преобразование в строку
    def __repr__(self):
        return f"<СonsultationTime({self.consultation_time_id}, {self.utc_hour}, {self.utc_minute})>"