import telebot, json
from typing import Callable
from botsys.core import strcontent
from botsys.db.model import Session, Database, KeyboardButton


# Билдер callack данных для кнопок
class ButtonDataBuilder:
    # Конструктор
    def __init__(self):
        self.db_session = Database.make_session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    # Метод генерации данных
    def make(self, command: str, **kwargs):
        rdata = {'c': command}              # Данные, отправляеммые в саму кнопку
        data = {}                           # Данные, отправляемые в БД

        # Формируем данные из kwargs
        for i in kwargs:
            if i == 'allowed_user_id':
                rdata['u'] = kwargs['allowed_user_id']
            else:
                data[i] = kwargs[i]

        # Добавляем данные в БД
        if(len(data) > 0):
            button_data = KeyboardButton(json.dumps(data, separators=(',', ':')))
            self.db_session.add(button_data)
            self.db_session.commit()

            # Формируем данные для самой кнопки
            rdata['d'] = button_data.id
        
        return json.dumps(rdata,  separators=(',', ':'))

    # Метод закрытия билдера
    def close(self):
        self.db_session.close()


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
                if self.__check_message_handler_limits(message):
                    action.callback(self, message, *action.args, **action.kwargs)
                self.__step_actions.remove(action)
                return


    # Обработчик callback запросов
    def __callback_query_handler(self, call: telebot.types.CallbackQuery):
        callback_data = json.loads(call.data)

        for command_info in self.__callback_query_commands:
            if callback_data['c'] == command_info.command:
                # Проверка пользователя на доступ к кнопке
                try:
                    if callback_data["u"] != call.from_user.id:
                        self.answer_callback_query(call.id, strcontent.NOTIFICATION_YOU_DO_NOT_HAVE_ACCESS_TO_THIS_MENU, True)
                        return
                except KeyError:
                    pass
                
                command_info.callback(self, call, callback_data)
                return
        
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
                    command.callback(self, message)
                    return

        # Обработка шагового действия пользователя
        self.__do_step_action(message)

    # Обработчик inline запросов
    def __inline_handler(self, inline: telebot.types.InlineQuery):
        if len(inline.query) > 0:
            query = inline.query.lower()                                        # Переводим запрос в нижний регистр
            for command_info in self.__inline_query_commands:
                if query.startswith(command_info.command):
                    command_info.callback(self, inline)
                    return

        # Если выход из метода не произошел, значит пользователь не ввел запрос или была получена неизвестная команда запроса
        # Выводим сообщение пользователю
        bot_username = self.get_me().username
        help_input_text_message_content = telebot.types.InputTextMessageContent(strcontent.MESSAGE_INLINE_HELP.format(bot_username))
        help_article = telebot.types.InlineQueryResultArticle('help', 'Помощь в этом чате', input_message_content=help_input_text_message_content)
        self.answer_inline_query(inline.id, [help_article], switch_pm_text=strcontent.BUTTON_INLINE_HELP_IN_PM, switch_pm_parameter='inlinehelp')

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
    def register_next_step_action(self, message: telebot.types.Message, callback: Callable, *args, **kwargs):
        chat_id = message.chat.id
        user_id = message.from_user.id

        self.__step_actions.append(StepAction(chat_id, user_id, callback, *args, **kwargs))

    # Очищает шаговое действие
    def clear_step_action(self, chat_id: int, user_id: int):
        for action in self.__step_actions:
            if action.chat_id == chat_id and action.user_id == user_id:
                self.__step_actions.remove(action)
