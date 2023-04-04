import telebot
from botsys.core import strcontent
from botsys.core.system import get_keyboard_row_list
from botsys.core.bot import Bot, KeyboardButtonDataBuilder
from botsys.db.model import Database, User, KeyboardButton
from botsys.db.behavior import check_user


def start_message_command(bot: Bot, message: telebot.types.Message):
    # База данных
    session = Database.make_session()
    db_user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()
    session.close()

    if db_user is None:
        bot.send_message(message.chat.id, strcontent.MESSAGE_START)
        bot.register_next_step_action(message.chat.id, message.from_user.id, registation, stage=1, reg_data={})
    else:
        # Сообщение о том, что пользователь уже прошел регистрацию
        bot.send_message(message.chat.id, strcontent.MESSAGE_ALREADY_REGISTERED)

def registation(bot: Bot, message: telebot.types.Message, stage, reg_data):
    # База данных
    session = Database.make_session()
    db_user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()

    if db_user is not None:
        # Сообщение о том, что пользователь уже прошел регистрацию
        bot.send_message(message.chat.id, strcontent.MESSAGE_ALREADY_REGISTERED)
        return

    if(len(message.text) <= 20):
        if stage == 1:
            reg_data['first_name'] = message.text[0].upper() + message.text[1:].lower()
            session.close()
            bot.send_message(message.chat.id, strcontent.MESSAGE_REGISTRATION_STAGE_1.format(first_name=reg_data['first_name']))
            bot.register_next_step_action(message.chat.id, message.from_user.id, registation, stage=2, reg_data=reg_data)
        elif stage == 2:
            reg_data['last_name'] = message.text[0].upper() + message.text[1:].lower()
            session.close()
            bot.send_message(message.chat.id, strcontent.MESSAGE_REGISTRATION_STAGE_2.format(first_name=reg_data['first_name'], last_name=reg_data['last_name']))
            bot.register_next_step_action(message.chat.id, message.from_user.id, registation, stage=3, reg_data=reg_data)
        elif stage == 3:
            reg_data['middle_name'] = message.text[0].upper() + message.text[1:].lower()
            db_user = User(message.from_user.id)
            db_user.first_name = reg_data['first_name']
            db_user.last_name = reg_data['last_name']
            db_user.middle_name = reg_data['middle_name']
            session.add(db_user)
            session.commit()

            markup = telebot.types.InlineKeyboardMarkup()
            with KeyboardButtonDataBuilder(session) as callback_data_builder:
                callback_data = callback_data_builder.set_callback_data(strcontent.COMMAND_CALLBACK_QUERY_CONSULTATION)
                markup.add(telebot.types.InlineKeyboardButton(text=strcontent.BUTTON_CONSULTATION, callback_data=callback_data))
            session.close()
            bot.send_message(message.chat.id, strcontent.MESSAGE_REGISTRATION_STAGE_3.format(first_name=reg_data['first_name'], last_name=reg_data['last_name'], middle_name=reg_data['middle_name']), reply_markup=markup)
    else:
        bot.send_message(message.chat.id, strcontent.MESSAGE_REGISTRATION_TOO_LONG_FIRST_NAME)
        bot.register_next_step_action(message.chat.id, message.from_user.id, registation, stage=stage, reg_data=reg_data)


class MenuCommand:
    @staticmethod
    def message_command(bot: Bot, message: telebot.types.Message):
        # База данных
        session = Database.make_session()
        db_user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()
        session.close()

        if db_user is None:
            bot.send_message(message.chat.id, strcontent.MESSAGE_NEED_REGISTRATION)
            return

        markup = telebot.types.InlineKeyboardMarkup()

        with KeyboardButtonDataBuilder() as callback_data_builder:
            callback_data = callback_data_builder.set_callback_data(strcontent.COMMAND_CALLBACK_QUERY_CONSULTATION)
            markup.add(telebot.types.InlineKeyboardButton(text=strcontent.BUTTON_CONSULTATION, callback_data=callback_data))
        
        bot.send_message(message.chat.id, 'Тестовое меню', reply_markup=markup)


class ConsultationCommand:
    @staticmethod
    def callback_query_command(bot: Bot, call: telebot.types.CallbackQuery, callback_data: dict):
        # База данных
        session = Database.make_session()
        db_user = session.query(User).filter_by(tg_user_id=call.from_user.id).first()
        session.close()

        if db_user is None:
            bot.answer_callback_query(call.id, strcontent.NOTIFICATION_NEED_REGISTRATION, show_alert=True)
            return

        stage = callback_data.get("stage", 1)
        data = callback_data.get("data", {})
        if stage == 1:
            inline_markup = telebot.types.InlineKeyboardMarkup()
            bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=inline_markup)
            
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CONSULTATION_TG_PHONE_NUMBER, request_contact=True))
            markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CONSULTATION_TELL_PHONE_NUMBER))
            markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
            bot.send_message(call.message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_1, reply_markup=markup)
            bot.register_next_step_action(call.message.chat.id, call.from_user.id, ConsultationCommand.get_phone_number, data=data)

    @staticmethod
    def get_phone_number(bot: Bot, message: telebot.types.Message, data, is_manual_input = False):
        # База данных
        session = Database.make_session()
        db_user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()
        session.close()

        if db_user is None:
            bot.send_message(message.chat.id, strcontent.MESSAGE_NEED_REGISTRATION)
            return

        if message.content_type == 'contact':
            data["phone_number"] = message.contact.phone_number
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            for row in get_keyboard_row_list(ConsultationCommand.__get_answers(1)):
                markup.row(*row)
            markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
            bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_2, reply_markup=markup)
            bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, data=data, q=1)
        elif message.content_type == 'text':
            if message.text == strcontent.BUTTON_CONSULTATION_TELL_PHONE_NUMBER:
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CONSULTATION_TG_PHONE_NUMBER, request_contact=True))
                markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TELL_PHONE_NUMBER, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_phone_number, data=data, is_manual_input=True)
            elif message.text == strcontent.BUTTON_CANCEL:
                markup = telebot.types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_CANCELED, reply_markup=markup)
            else:
                if is_manual_input:
                    if len(message.text) <= 10 and ConsultationCommand.__validate_phone_number(message.text):
                        data["phone_number"] = f"7{message.text}"
                        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                        for row in get_keyboard_row_list(ConsultationCommand.__get_answers(1)):
                            markup.row(*row)
                        markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
                        bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_2, reply_markup=markup)
                        bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, data=data, q=1)
                    else:
                        bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TELL_PHONE_NUMBER)
                        bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_phone_number, data=data, is_manual_input=True)
                else:
                    bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_HELP_1)
                    bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_phone_number, data=data)
        else:
            bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_HELP_1)
            bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_phone_number, data=data)

    @staticmethod
    def get_answers_to_survey(bot: Bot, message: telebot.types.Message, data, q):
        # База данных
        session = Database.make_session()
        db_user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()
        session.close()

        if db_user is None:
            bot.send_message(message.chat.id, strcontent.MESSAGE_NEED_REGISTRATION)
            return
        
        if message.text == strcontent.BUTTON_CANCEL:
            markup = telebot.types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_CANCELED, reply_markup=markup)
        elif q == 1:
            if message.text in ConsultationCommand.__get_answers(1):
                data["lang_level"] = message.text
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_3, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, data=data, q=2)
            else:
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                for row in get_keyboard_row_list(ConsultationCommand.__get_answers(1)):
                    markup.row(*row)
                markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_2, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, data=data, q=1)
        elif q == 2:
            if len(message.text) <= 100:
                data['hsk_exam'] = message.text
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_4)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, data=data, q=3)
            else:
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TOO_LONG_ANSWER)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, data=data, q=2)
        elif q == 3:
            if len(message.text) <= 100:
                data['purpose'] = message.text
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                for row in get_keyboard_row_list(ConsultationCommand.__get_answers(2), 2):
                    markup.row(*row)
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_5, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, data=data, q=4)
            else:
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TOO_LONG_ANSWER)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, data=data, q=3)
        elif q == 4:
            if message.text in ConsultationCommand.__get_answers(2):
                data['way_now'] = message.text
                markup = telebot.types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_6, reply_markup=markup)
                bot.send_message(message.chat.id, str(data))
            else:
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                for row in get_keyboard_row_list(ConsultationCommand.__get_answers(2), 2):
                    markup.row(*row)
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_5, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, data=data, q=4)
        else:
            markup = telebot.types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_CREATION_ERROR, reply_markup=markup)

    @staticmethod
    def __validate_phone_number(phone_number: str) -> bool:
        is_correct = True
        numbers = list('0123456789')
        for s in phone_number:
            if not (s in numbers):
                is_correct = False
                break
        return is_correct
    
    @staticmethod
    def __get_answers(q: int):
        if q == 1:
            return [
                strcontent.BUTTON_CONSULTATION_ANSWER_HSK1, strcontent.BUTTON_CONSULTATION_ANSWER_HSK2,
                strcontent.BUTTON_CONSULTATION_ANSWER_HSK3, strcontent.BUTTON_CONSULTATION_ANSWER_HSK4,
                strcontent.BUTTON_CONSULTATION_ANSWER_HSK5, strcontent.BUTTON_CONSULTATION_ANSWER_HSK6,
                strcontent.BUTTON_CONSULTATION_ANSWER_ZERO, strcontent.BUTTON_CONSULTATION_ANSWER_IDK
            ]
        elif q == 2:
            return [
                strcontent.BUTTON_CONSULTATION_ANSWER_NO_HOW, strcontent.BUTTON_CONSULTATION_ANSWER_ONLINE_СOURSES,
                strcontent.BUTTON_CONSULTATION_ANSWER_ONLINE_TEACHER, strcontent.BUTTON_CONSULTATION_ANSWER_OFFLINE_TEACHER,
                strcontent.BUTTON_CONSULTATION_ANSWER_GROUP_LESSONS, strcontent.BUTTON_CONSULTATION_ANSWER_INDEPENDENTLY
            ]
        else:
            return []
