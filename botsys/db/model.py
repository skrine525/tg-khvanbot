from sqlalchemy import Column, ForeignKey, SmallInteger, Integer, BigInteger, String, Boolean, JSON, VARCHAR, UUID, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship
import datetime, uuid


Base = declarative_base() # Базовый класс модели

# Системная таблица для хранения данных внутри callback кнопок
class KeyboardButton(Base):
    __tablename__ = 'keyboard_buttons'

    # Столбцы
    button_id = Column(UUID, primary_key=True, default=uuid.uuid4)                              # UUID кнопки
    creation_time = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)         # Время создания записи
    data = Column(JSON, nullable=False)                                                         # JSON данные кнопки

    # Конструктор
    def __init__(self, data: dict):
        self.data = data

    # Преобразование в строку
    def __repr__(self):
        return f"<KeyboardButton('{self.button_id}')>"


# Пользователь
class User(Base):
    __tablename__ = 'users'

    # Столбцы
    user_id = Column(BigInteger, primary_key=True)                                              # Числовой идентификатор
    tg_user_id = Column(BigInteger, unique=True, nullable=False)                                # Идентификатор аккаунта Telegram
    first_name = Column(VARCHAR(20), nullable=False)                                            # Имя пользователя
    last_name = Column(VARCHAR(20), default=None)                                               # Фамилия пользователя
    middle_name = Column(VARCHAR(20), default=None)                                             # Отчество пользователя
    registration_time = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)     # Время регистрации пользователя
    tz_utc_offset = Column(SmallInteger, nullable=False, default=0)                             # Часовой пояс относительно UTC

    # Отношения
    role = relationship('UserRole', backref='user', uselist=False, cascade="all,delete")
    consultations = relationship('Consultation', backref='user', uselist=True, cascade="all,delete", lazy="dynamic")

    # Конструктор
    def __init__(self, tg_user_id: int):
        self.tg_user_id = tg_user_id

    # Преобразование в строку
    def __repr__(self):
        fullname = self.get_full_name()
        return f"<User({self.user_id}, {self.tg_user_id}, '{fullname}')>"
    
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
    ROLE_ADMIN = 'admin'

    # Столбцы
    user_role_id = Column(BigInteger, primary_key=True)                                     # Идентификатор роли пользователя
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, unique=True)  # Идентификатор пользователя
    role = Column(VARCHAR(10), nullable=False)                                              # Роль пользователя
    acquisition_time = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)  # Временная метка получения роли

    # Отношения
    admin = relationship('Admin', backref='role', uselist=False, cascade="all,delete")

    # Конструктор
    def __init__(self, user_id: int, role: str):
        self.user_id = user_id
        self.role = role

    # Преобразование в строку
    def __repr__(self):
        return f"<UserRole({self.user_role_id}, {self.user_id}, '{self.role}')>"
    
    # Проверка пользователя на роль Администратор
    def is_admin(self):
        return (self.role == UserRole.ROLE_ADMIN)
    

# Администраторы
class Admin(Base):
    __tablename__ = 'admins'

    # Столбцы
    admin_id = Column(BigInteger, primary_key=True)                                                         # Идентификатор администратора
    user_role_id = Column(BigInteger, ForeignKey("user_roles.user_role_id"), nullable=False, unique=True)   # Идентификатор роли пользователя
    is_consultation_admin = Column(Boolean, nullable=False, default=False)                                  # Является ли администратором консультаций

    # Конструктор
    def __init__(self, user_role_id: int):
        self.user_role_id = user_role_id

    # Преобразование в строку
    def __repr__(self):
        return f"<Admin({self.admin_id}, {self.user_role_id})>"

# Записи на консультацию
class Consultation(Base):
    __tablename__ = 'consultations'

    # Столбцы
    consultation_id = Column(BigInteger, primary_key=True)                                  # Идентификатор консультации
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)               # Идентификатор пользователя
    creation_time = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)     # Время создания записи на консультацию
    is_processed = Column(Boolean, nullable=False, default=False)                           # Статус консультации
    age = Column(SmallInteger, nullable=False)                                              # Анкета: Возраст
    phone_number = Column(VARCHAR(20), nullable=False)                                      # Анкета: Номер телефона
    lang_level = Column(VARCHAR(50), nullable=False)                                        # Анкета: Уровень языка
    hsk_exam = Column(VARCHAR(100), nullable=False)                                         # Анкета: Экзамен HSK
    purpose = Column(VARCHAR(100), nullable=False)                                          # Анкета: Цель изучения
    way_now = Column(VARCHAR(50), nullable=False)                                           # Анкета: Способ изучения сейчас

    # Отношения
    notification = relationship("ConsultationNotification", backref="consultation", uselist=False, cascade="all,delete")
    appointment_time = relationship("ConsultationAppointmentTime", backref="consultation", uselist=False)

    # Конструктор
    def __init__(self, user_id: int, age: int, phone_number: str, lang_level: str, hsk_exam: str, purpose: str, way_now: str):
        self.user_id = user_id
        self.age = age
        self.phone_number = phone_number
        self.lang_level = lang_level
        self.hsk_exam = hsk_exam
        self.purpose = purpose
        self.way_now = way_now

    # Преобразование в строку
    def __repr__(self):
        return f"<Сonsultation({self.consultation_id}, {self.user_id})>"


# Уведомления о консультациях
class ConsultationNotification(Base):
    __tablename__ = 'consultation_notifications'

    # Столбцы
    cn_id = Column(BigInteger, primary_key=True)                                                                    # Идентификатор уведомления
    consultation_id = Column(BigInteger, ForeignKey("consultations.consultation_id"), unique=True, nullable=False)  # Идентификатор консультации
    tg_chat_id = Column(BigInteger, nullable=False)                                                                 # Идентификатор чата Телеграмма
    tg_message_id = Column(BigInteger, nullable=False)                                                              # Идентификатор сообщения Телеграмма

    # Конструктор
    def __init__(self, consultation_id: int, tg_chat_id: int, tg_message_id: int):
        self.consultation_id = consultation_id
        self.tg_chat_id = tg_chat_id
        self.tg_message_id = tg_message_id

    # Преобразование в строку
    def __repr__(self):
        return f"<ConsultationNotification({self.cn_id}, {self.consultation_id})>"
    
# Таблица списка времён, которые доступны во время записи на консультацию
class ConsultationAppointmentTime(Base):
    __tablename__ = 'consultation_appointment_times'

    # Столбцы
    cat_id = Column(BigInteger, primary_key=True)                                                                                           # Идентификатор времени приёма на консультацию
    consultation_id = Column(BigInteger, ForeignKey("consultations.consultation_id", ondelete="SET NULL"), unique=True, nullable=True)      # Идентификатор консультации
    appointment_time = Column(TIMESTAMP, unique=True, nullable=False)                                                                       # Время проведения консультации

    # Конструктор
    def __init__(self, appointment_time: datetime.datetime):
        self.appointment_time = appointment_time

    # Преобразование в строку
    def __repr__(self):
        return f"<ConsultationAppointmentTime({self.cat_id}, {self.consultation_id}, '{self.appointment_time}')>"