import telebot, logging
import botsys.core.strcontent as strcontent
from typing import Callable
from botsys.db.model import KeyboardButton
from botsys.core.system import SystemPaths
from botsys.db.behavior import Session, Database


# Настройка логирования
logger = telebot.logger
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(filename)s:%(lineno)d %(threadName)s] [%(name)s] [%(levelname)s] - %(message)s')
file_handler = logging.FileHandler(SystemPaths.LOG_FILE, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.handlers.clear()
logger.addHandler(file_handler)


# Билдер callack данных для кнопок
class InlineKeyboardDataBuilder:
    # Конструктор
    def __init__(self, session: Session):
        self.__session = session
        self.__db_buttons = []

    # Метод добавления callback_data в список
    def add_callback_data(self, **kwargs):
        button = KeyboardButton(kwargs)
        self.__session.add(button)
        self.__db_buttons.append(button)

    # Принимает данные, фиксирует в сущности KeyboardButton и возвращает button_id
    def build_single_callback_data(self, **kwargs):
        button = KeyboardButton(kwargs)
        self.__session.add(button)
        self.__session.commit()
        return str(button.button_id)
        
    # Фиксирует данные в сущности KeyboardButton и возвращает список button_id
    def build(self) -> list:
        self.__session.commit()
        ids = []
        for button in self.__db_buttons:
            ids.append(str(button.button_id))
        self.__db_buttons.clear()
        return ids


# Базовый класс, хранящий ифномарцию о команде
class BaseCommand:
    def __init__(self, command: str, callback: Callable):
        self.command: str = command
        self.callback: Callable = callback


# Класс, хранящий информацию о текстовой команде
class MessageCommand(BaseCommand):
    def __init__(self, command: str, callback: Callable, description: str, add_to_menu: bool):
        super().__init__(command, callback)
        self.description: str = description
        self.add_to_menu: bool = add_to_menu

    @property
    def slash_сommand(self) -> str:
        return f"/{self.command}"

# Класс, хранящий информацию о шаговом действии
class StepAction:
    def __init__(self, chat_id: int, user_id: int, callback: Callable, *args, **kwargs):
        self.chat_id: int = chat_id
        self.user_id: int = user_id
        self.callback: Callable = callback
        self.args: list = args
        self.kwargs: dict = kwargs


class Bot(telebot.TeleBot):
    # Консруктор
    def __init__(self, token: str):
        super().__init__(token)                         # Вызов конструктора TeleBot
        self.__message_commands: list = []              # Инициализация списка текстовых команд
        self.__callback_query_commands: list = []       # Инициализация списка команд callback запросов
        self.__inline_query_commands: list = []         # Инициализация списка команд inline запросов
        self.__step_actions: list = []                  # Инициализация списка шаговых действий

        # Регистрация обработчика сообщений
        @self.message_handler(func=lambda message: True, content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'location', 'contact'])
        def message_handler(message: telebot.types.Message):
            self.__message_handler(message)

        # Регистрация обработчика callback запросов
        @self.callback_query_handler(func=lambda call: True)
        def callback_query_handler(call: telebot.types.CallbackQuery):
            self.__callback_query_handler(call)

        # Регистрация обработчика inline запросов
        @self.inline_handler(lambda query: True)
        def inline_handler(inline: telebot.types.InlineQuery):
            self.__inline_handler(inline)

    # Выполняет проверку ограничение обработчика сообщений
    def __check_message_handler_limits(self, message: telebot.types.Message):
        # Проверка на анонимного пользователя в беседах
        # ID: 1087968824
        # Username: GroupAnonymousBot
        if message.from_user.id == 1087968824:
            self.send_message(message.chat.id, strcontent.MESSAGE_COMMANDS_NOT_AVAILABLE_TO_ANONYMOUS_IN_GROUP, reply_to_message_id=message.id)
            return False

        # Если все ограничения пройдены, то возвращаем True
        return True

    # Выполняет ближайшее шаговое действие пользователя и удаляет его из памяти
    def __do_step_action(self, message: telebot.types.Message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        for action in self.__step_actions:
            if action.chat_id == chat_id and action.user_id == user_id:
                self.__step_actions.remove(action) # Иногда выдает баги, когда в массиве два степ экшена
                if self.__check_message_handler_limits(message):
                    session = Database.make_session()
                    action.callback(self, message, session, *action.args, **action.kwargs)
                    session.close()
                return


    # Обработчик callback запросов
    def __callback_query_handler(self, call: telebot.types.CallbackQuery):
        session = Database.make_session()
        button = session.query(KeyboardButton).filter_by(button_id=call.data).first()

        if button is None:
            self.edit_message_text(strcontent.MESSAGE_CONTENT_NOT_AVAILABLE, call.message.chat.id, call.message.id)
            session.close()
            return
        
        callback_data = button.data

        for command_info in self.__callback_query_commands:
            if callback_data['command'] == command_info.command:
                # Проверка пользователя на доступ к кнопке
                try:
                    if callback_data["allowed_user_id"] != call.from_user.id:
                        self.answer_callback_query(call.id, strcontent.NOTIFICATION_YOU_DO_NOT_HAVE_ACCESS_TO_THIS_MENU, True)
                        session.close()
                        return
                except KeyError:
                    pass
                
                command_info.callback(self, call, session, callback_data)
                session.close()
                return
        
        # Закрываем сессию БД
        session.close()
        
        # Если выход из метода не произошел, значит была получена неизвестная команда
        # Выводим ошибку пользователю
        self.answer_callback_query(call.id, strcontent.NOTIFICATION_UNKNOWN_COMMAND, True)

    # Обработчик сообщений
    def __message_handler(self, message: telebot.types.Message):
        # Обработка команд
        if message.content_type == "text":
            for command in self.__message_commands:
                if message.text.startswith(command.slash_сommand) and self.__check_message_handler_limits(message):
                    self.clear_step_action(message.chat.id, message.from_user.id)
                    session = Database.make_session()
                    command.callback(self, message, session)
                    session.close()
                    return

        # Обработка шагового действия пользователя
        self.__do_step_action(message)

    # Обработчик inline запросов
    def __inline_handler(self, inline: telebot.types.InlineQuery):
        if len(inline.query) > 0:
            query = inline.query.lower()                                        # Переводим запрос в нижний регистр
            for command_info in self.__inline_query_commands:
                if query.startswith(command_info.command):
                    session = Database.make_session()
                    command_info.callback(self, inline)
                    session.close()
                    return

        # Если выход из метода не произошел, значит пользователь не ввел запрос или была получена неизвестная команда запроса
        # Выводим сообщение пользователю
        self.answer_inline_query(inline.id, [])

    # Регистрирует новую текстовую команду
    def register_message_command(self, command: str, callback: Callable, description = '', add_to_menu: bool = False):
        command = command.lower()                                               # Переводим команду в нижний регистр
        # Поиск команды, если найдена, то возращаем False
        for command_info in self.__message_commands:
            if command_info.command == command:
                return False

        # Добавляем команду
        self.__message_commands.append(MessageCommand(command, callback, description, add_to_menu))
        return True

    # Регистрирует новую команду callback запроса
    def register_callback_query_command(self, command: str, callback: Callable):
        command = command.lower()      
        # Поиск команды, если найдена, то возращаем False
        for command_info in self.__callback_query_commands:
            if command_info.command == command:
                return False                                                    # Переводим команду в нижний регистр

        # Добавляем команду
        self.__callback_query_commands.append(BaseCommand(command, callback))
        return True

    # Регистрирует новую команду inline запроса
    def register_inline_query_command(self, command: str, callback: Callable):
        command = command.lower()                                               # Переводим команду в нижний регистр
         # Поиск команды, если найдена, то возращаем False
        for command_info in self.__inline_query_commands:
            if command_info.command == command:
                return False                                                    # Переводим команду в нижний регистр

        # Добавляем команду
        self.__inline_query_commands.append(BaseCommand(command, callback))
        return True

    # Устанавливает команды и их описание в меню команд бота
    def set_commands_menu(self):
        bot_commands = []
        for i in self.__message_commands:
            if i.add_to_menu:
                bot_commands.append(telebot.types.BotCommand(i.command, i.description))
        self.set_my_commands(bot_commands)

    # Устанавливает следущее шаговое действие
    def register_next_step_action(self, chat_id: int, user_id: int, callback: Callable, *args, **kwargs):
        self.clear_step_action(chat_id, user_id)                                            # Сначала чистим для пользователя в чате степ экшены
        self.__step_actions.append(StepAction(chat_id, user_id, callback, *args, **kwargs)) # А теперь добавляем

    # Очищает шаговое действие
    def clear_step_action(self, chat_id: int, user_id: int):
        for action in self.__step_actions:
            if action.chat_id == chat_id and action.user_id == user_id:
                self.__step_actions.remove(action)

    # Позволяет получить уникальный токен inline кнопок
    def get_inline_keyboard_token(self):
        return self.__inline_keyboard_token
