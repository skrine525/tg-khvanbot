import telebot, datetime
from botsys.core import strcontent
from botsys.core.system import get_keyboard_row_list, escape_markdownv2_text
from botsys.core.bot import Bot, InlineKeyboardDataBuilder
from botsys.db.model import User, Сonsultation, СonsultationTime
from botsys.db.behavior import Database


class RegistrationCommand:
    @staticmethod
    def start_message_command(bot: Bot, message: telebot.types.Message):
        # База данных
        session = Database.make_session()
        db_user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()
        session.close()

        if db_user is None:
            bot.send_message(message.chat.id, strcontent.MESSAGE_START, parse_mode="MarkdownV2")
            bot.register_next_step_action(message.chat.id, message.from_user.id, RegistrationCommand.registation, stage=1, reg_data={})
        else:
            # Сообщение о том, что пользователь уже прошел регистрацию
            bot.send_message(message.chat.id, strcontent.MESSAGE_ALREADY_REGISTERED)

    @staticmethod
    def registation(bot: Bot, message: telebot.types.Message, stage, reg_data):
        # База данных
        session = Database.make_session()
        db_user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()

        if db_user is not None:
            # Сообщение о том, что пользователь уже прошел регистрацию
            bot.send_message(message.chat.id, strcontent.MESSAGE_ALREADY_REGISTERED)
            return

        
        if stage == 1:
            if len(message.text) > 20:
                bot.send_message(message.chat.id, strcontent.MESSAGE_REGISTRATION_TOO_LONG_FIRST_NAME)
                bot.register_next_step_action(message.chat.id, message.from_user.id, RegistrationCommand.registation, stage=stage, reg_data=reg_data)
                return
            elif not RegistrationCommand.__validate_name(message.text):
                bot.send_message(message.chat.id, strcontent.MESSAGE_REGISTRATION_PROHIBITED_SYMBOLS_CANNOT_BE_USED, parse_mode="MarkdownV2")
                bot.register_next_step_action(message.chat.id, message.from_user.id, RegistrationCommand.registation, stage=stage, reg_data=reg_data)
                return

            reg_data['first_name'] = message.text[0].upper() + message.text[1:].lower()

            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            timezones = [
                strcontent.BUTTON_TIMEZONE_MSC_M1, strcontent.BUTTON_TIMEZONE_MSC_P1,
                strcontent.BUTTON_TIMEZONE_MSC_P2, strcontent.BUTTON_TIMEZONE_MSC_P3,
                strcontent.BUTTON_TIMEZONE_MSC_P4, strcontent.BUTTON_TIMEZONE_MSC_P5,
                strcontent.BUTTON_TIMEZONE_MSC_P6, strcontent.BUTTON_TIMEZONE_MSC_P7,
                strcontent.BUTTON_TIMEZONE_MSC_P8, strcontent.BUTTON_TIMEZONE_MSC_P9,
                strcontent.BUTTON_TIMEZONE_MSC
            ]
            for row in get_keyboard_row_list(timezones, 5):
                markup.row(*row)
            session.close()

            bot.send_message(message.chat.id, strcontent.MESSAGE_REGISTRATION_STAGE_1.format(first_name=reg_data['first_name']), parse_mode="MarkdownV2", reply_markup=markup)
            bot.register_next_step_action(message.chat.id, message.from_user.id, RegistrationCommand.registation, stage=2, reg_data=reg_data)
        elif stage == 2:
            timezone = 0
            if message.text == strcontent.BUTTON_TIMEZONE_MSC_M1:
                timezone = -1
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P1:
                timezone = 1
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P2:
                timezone = 2
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P3:
                timezone = 3
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P4:
                timezone = 4
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P5:
                timezone = 5
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P6:
                timezone = 6
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P7:
                timezone = 7
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P8:
                timezone = 8
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P9:
                timezone = 9
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC:
                pass
            else:
                bot.send_message(message.chat.id, strcontent.MESSAGE_REGISTRATION_STAGE_1.format(first_name=reg_data['first_name']), parse_mode="MarkdownV2", reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, RegistrationCommand.registation, stage=2, reg_data=reg_data)
                return
            
            db_user = User(message.from_user.id)
            db_user.first_name = reg_data['first_name']
            db_user.tz_msc_offset = timezone
            session.add(db_user)
            session.commit()
            
            inline_markup = telebot.types.InlineKeyboardMarkup()
            keyboard_data_builder = InlineKeyboardDataBuilder(bot, session)
            callback_data = keyboard_data_builder.build_single_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_CONSULTATION)
            inline_markup.add(telebot.types.InlineKeyboardButton(text=strcontent.BUTTON_CONSULTATION, callback_data=callback_data))
            session.close()

            markup = telebot.types.ReplyKeyboardRemove()

            # Экранирование спецсимволов MarkdownV2
            timezone_text = message.text.replace("+", "\\+").replace("-", "\\-")

            bot.send_message(message.chat.id, strcontent.MESSAGE_REGISTRATION_STAGE_2.format(first_name=reg_data['first_name'], timezone=timezone_text), parse_mode="MarkdownV2", reply_markup=markup)
            bot.send_message(message.chat.id, strcontent.MESSAGE_OFFER_CONSULTATION, reply_markup=inline_markup)

    @staticmethod
    def __validate_name(name: str):
        is_correct = True
        symbols = list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя_abcdefghijklmnopqrstuvwxyz')
        for s in name.lower():
            if not (s in symbols):
                is_correct = False
                break
        return is_correct

class MenuCommand:
    @staticmethod
    def message_command(bot: Bot, message: telebot.types.Message):
        # База данных
        session = Database.make_session()
        db_user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()

        if db_user is None:
            bot.send_message(message.chat.id, strcontent.MESSAGE_NEED_REGISTRATION)
            return

        markup = telebot.types.InlineKeyboardMarkup()
        keyboard_data_builder = InlineKeyboardDataBuilder(bot, session)
        buttons = []

        if db_user.role is None:
            keyboard_data_builder.add_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_CONSULTATION)
            buttons.append(strcontent.BUTTON_CONSULTATION)

        buttons_ids = keyboard_data_builder.build()
        session.close()

        for i in range(len(buttons)):
            markup.add(telebot.types.InlineKeyboardButton(buttons[i], callback_data=buttons_ids[i]))

        bot.send_message(message.chat.id, strcontent.MESSAGE_MENU, reply_markup=markup)


class ConsultationCommand:
    @staticmethod
    def callback_query_command(bot: Bot, call: telebot.types.CallbackQuery, callback_data: dict):
        # База данных
        session = Database.make_session()
        db_user = session.query(User).filter_by(tg_user_id=call.from_user.id).first()

        if db_user is None:
            bot.answer_callback_query(call.id, strcontent.NOTIFICATION_NEED_REGISTRATION)
            return
        elif db_user.consultations.filter_by(is_processed=False).first() is not None:
            bot.answer_callback_query(call.id, strcontent.NOTIFICATION_YOU_HAVE_ALREADY_ACTIVE_CONSULTATION, show_alert=True)
            return
        elif db_user.role is not None:
            bot.answer_callback_query(call.id, strcontent.NOTIFICATION_YOU_HAVE_NO_ACCESS)
            return

        stage = callback_data.get("stage", 1)
        form = callback_data.get("form", {})
        if stage < 0:
            session.close()
            bot.edit_message_text(strcontent.MESSAGE_CONSULTATION_CANCELED, call.message.chat.id, call.message.id)
        elif stage == 1:
            session.close()
            inline_markup = telebot.types.InlineKeyboardMarkup()
            bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=inline_markup)
            
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CONSULTATION_TG_PHONE_NUMBER, request_contact=True))
            markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CONSULTATION_TELL_PHONE_NUMBER))
            #markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
            bot.send_message(call.message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_1, reply_markup=markup)
            bot.register_next_step_action(call.message.chat.id, call.from_user.id, ConsultationCommand.get_phone_number, form=form)
        elif stage == 2:
            tz_timedelta = datetime.timedelta(hours=db_user.tz_msc_offset + 3)

            utc_time = datetime.datetime.utcnow()
            user_time = utc_time + tz_timedelta
            interval = datetime.timedelta(days=1)

            callback_data_builder = InlineKeyboardDataBuilder(bot, session)
            button_text = []

            for i in range(7):
                user_time = user_time + interval

                callback_data = {
                    "command": callback_data["command"],
                    "stage": 3,
                    "form": callback_data["form"],
                    "time": {"day": user_time.day, "month": user_time.month, "year": user_time.year}
                }
                callback_data_builder.add_callback_data(**callback_data)

                date_text = f"0{user_time.day}" if user_time.day < 10 else f"{user_time.day}"
                date_text = f"{date_text}.0{user_time.month}" if user_time.month < 10 else f"{date_text}.{user_time.month}"
                button_text.append(date_text)
            callback_data_builder.add_callback_data(command=callback_data["command"], stage=-1)
            button_ids = callback_data_builder.build()
            session.close()

            buttons = []
            for i in range(len(button_text)):
                buttons.append(telebot.types.InlineKeyboardButton(button_text[i], callback_data=button_ids[i]))

            markup = telebot.types.InlineKeyboardMarkup()
            for row in get_keyboard_row_list(buttons):
                markup.row(*row)
            #markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_CANCEL, callback_data=button_ids[-1]))

            bot.edit_message_text(strcontent.MESSAGE_CONSULTATION_SELECT_TIME_2, call.message.chat.id, call.message.id, reply_markup=markup)
        elif stage == 3:
            tz_timedelta = datetime.timedelta(hours=db_user.tz_msc_offset + 3)

            date_day = callback_data["time"]["day"]
            date_month = callback_data["time"]["month"]
            date_year = callback_data["time"]["year"]
            date_text = f"0{date_day}" if date_day < 10 else f"{date_day}"
            date_text = f"{date_text}\\.0{date_month}" if date_month < 10 else f"{date_text}\\.{date_month}"

            utc_time = datetime.datetime.utcnow()

            callback_data_builder = InlineKeyboardDataBuilder(bot, session)
            button_text = []
            consultation_times = session.query(СonsultationTime).order_by(СonsultationTime.utc_hour, СonsultationTime.utc_minute).all()

            for consultation_time in consultation_times:
                user_time = datetime.datetime(
                    year=utc_time.year, month=utc_time.month, day=utc_time.day,
                    hour=consultation_time.utc_hour, minute=consultation_time.utc_minute
                )
                user_time = user_time + tz_timedelta

                display_hour = user_time.hour
                display_minute = user_time.minute

                user_utc_time = datetime.datetime(
                    year=date_year, month=date_month, day=date_day,
                    hour=user_time.hour, minute=user_time.minute
                )
                user_utc_time = user_utc_time - tz_timedelta

                if user_utc_time > utc_time:
                    time_text = f"0{display_hour}" if display_hour < 10 else f"{display_hour}"
                    time_text = f"{time_text}:0{display_minute}" if display_minute < 10 else f"{time_text}:{display_minute}"
                    button_text.append(time_text)

                    callback_data = {
                        "command": callback_data["command"],
                        "stage": 4,
                        "form": callback_data["form"],
                        "time": {
                            "day": user_utc_time.day,
                            "month": user_utc_time.month,
                            "year": user_utc_time.year,
                            "hour": user_utc_time.hour,
                            "minute": user_utc_time.minute
                        }
                    }
                    callback_data_builder.add_callback_data(**callback_data)

            callback_data_builder.add_callback_data(command=callback_data["command"], stage=2, form=callback_data["form"])  
            #callback_data_builder.add_callback_data(command=callback_data["command"], stage=-1)
            button_ids = callback_data_builder.build()
            session.close()

            buttons = []
            for i in range(len(button_text)):
                buttons.append(telebot.types.InlineKeyboardButton(button_text[i], callback_data=button_ids[i]))

            markup = telebot.types.InlineKeyboardMarkup()
            for row in get_keyboard_row_list(buttons):
                markup.row(*row)
            #markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_CANCEL, callback_data=button_ids[-1]))
            markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_BACK, callback_data=button_ids[-1]))

            bot.edit_message_text(strcontent.MESSAGE_CONSULTATION_SELECT_TIME_3.format(date=date_text), call.message.chat.id, call.message.id, reply_markup=markup, parse_mode="MarkdownV2")
        elif stage == 4:
            tz_timedelta = datetime.timedelta(hours=db_user.tz_msc_offset + 3)

            user_utc_time = datetime.datetime(
                year=callback_data["time"]["year"], month=callback_data["time"]["month"],
                day=callback_data["time"]["day"], hour=callback_data["time"]["hour"],
                minute=callback_data["time"]["minute"], second=0, microsecond=0
            )

            display_time = user_utc_time + tz_timedelta
            date_text = f"0{display_time.day}" if display_time.day < 10 else f"{display_time.day}"
            date_text = f"{date_text}.0{display_time.month}" if display_time.month < 10 else f"{date_text}.{display_time.month}"
            time_text = f"0{display_time.hour}" if display_time.hour < 10 else f"{display_time.hour}"
            time_text = f"{time_text}:0{display_time.minute}" if display_time.minute < 10 else f"{time_text}:{display_time.minute}"

            callback_data_builder = InlineKeyboardDataBuilder(bot, session)
            callback_data_builder.add_callback_data(
                command=callback_data["command"], stage=5,
                form=callback_data["form"], time=callback_data["time"]
            )
            callback_data_builder.add_callback_data(
                command=callback_data["command"], stage=2,
                form=callback_data["form"]
            )
            callback_data_builder.add_callback_data(command=callback_data["command"], stage=-1)
            button_ids = callback_data_builder.build()

            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_CONFIRM, callback_data=button_ids[0]))
            markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_CONSULTATION_CHANGE_TIME, callback_data=button_ids[1]))
            markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_CANCEL, callback_data=button_ids[2]))

            embedded_text_list = {'date': date_text, 'time': time_text, 'user_name': db_user.get_full_name()}
            embedded_text_list = {**embedded_text_list, **callback_data["form"]}
            for i in embedded_text_list:
                embedded_text_list[i] = escape_markdownv2_text(embedded_text_list[i])

            text = strcontent.MESSAGE_CONSULTATION_CONFIRMATION.format(**embedded_text_list)
            bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup, parse_mode="MarkdownV2")
            session.close()
        elif stage == 5:
            consultation_time = datetime.datetime(
                year=callback_data["time"]["year"], month=callback_data["time"]["month"],
                day=callback_data["time"]["day"], hour=callback_data["time"]["hour"],
                minute=callback_data["time"]["minute"], second=0, microsecond=0
            )
            db_consultation = Сonsultation(
                db_user.user_id, callback_data["form"]["phone_number"],
                callback_data["form"]["lang_level"], callback_data["form"]["hsk_exam"],
                callback_data["form"]["purpose"], callback_data["form"]["way_now"], consultation_time
            )

            session.add(db_consultation)
            session.commit()

            text = strcontent.MESSAGE_CONSULTATION_SENT.format(consultation_id=db_consultation.consultation_id)
            bot.edit_message_text(text, call.message.chat.id, call.message.id)


    @staticmethod
    def get_phone_number(bot: Bot, message: telebot.types.Message, form, is_manual_input = False):
        # База данных
        session = Database.make_session()
        db_user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()
        session.close()

        if db_user is None:
            bot.send_message(message.chat.id, strcontent.MESSAGE_NEED_REGISTRATION)
            return

        if message.content_type == 'contact':
            form["phone_number"] = message.contact.phone_number
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            for row in get_keyboard_row_list(ConsultationCommand.__get_answers(1)):
                markup.row(*row)
            #markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
            bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_2, reply_markup=markup)
            bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=1)
        elif message.content_type == 'text':
            if message.text == strcontent.BUTTON_CONSULTATION_TELL_PHONE_NUMBER:
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CONSULTATION_TG_PHONE_NUMBER, request_contact=True))
                #markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TELL_PHONE_NUMBER, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_phone_number, form=form, is_manual_input=True)
            elif message.text == strcontent.BUTTON_CANCEL:
                markup = telebot.types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_CANCELED, reply_markup=markup)
            else:
                if is_manual_input:
                    if len(message.text) == 10 and ConsultationCommand.__validate_phone_number(message.text):
                        form["phone_number"] = f"7{message.text}"
                        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                        for row in get_keyboard_row_list(ConsultationCommand.__get_answers(1)):
                            markup.row(*row)
                        #markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
                        bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_2, reply_markup=markup)
                        bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=1)
                    else:
                        bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TELL_PHONE_NUMBER)
                        bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_phone_number, form=form, is_manual_input=True)
                else:
                    bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_HELP_1)
                    bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_phone_number, form=form)
        else:
            bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_HELP_1)
            bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_phone_number, form=form)

    @staticmethod
    def get_answers_to_survey(bot: Bot, message: telebot.types.Message, form, q):
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
                form["lang_level"] = message.text
                markup = telebot.types.ReplyKeyboardRemove()
                #markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                #markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_3, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=2)
            else:
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                for row in get_keyboard_row_list(ConsultationCommand.__get_answers(1)):
                    markup.row(*row)
                #markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_2, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=1)
        elif q == 2:
            if len(message.text) <= 100:
                form['hsk_exam'] = message.text
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_4)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=3)
            else:
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TOO_LONG_ANSWER)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=2)
        elif q == 3:
            if len(message.text) <= 100:
                form['purpose'] = message.text
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                for row in get_keyboard_row_list(ConsultationCommand.__get_answers(2), 2):
                    markup.row(*row)
                #markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_5, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=4)
            else:
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TOO_LONG_ANSWER)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=3)
        elif q == 4:
            if message.text in ConsultationCommand.__get_answers(2):
                form['way_now'] = message.text
                markup = telebot.types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_6, reply_markup=markup)
                markup = telebot.types.InlineKeyboardMarkup()
                keyboard_data_builder = InlineKeyboardDataBuilder(bot, session)
                callback_data = keyboard_data_builder.build_single_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_CONSULTATION, stage=2, form=form)
                markup.add(telebot.types.InlineKeyboardButton(text=strcontent.BUTTON_CONSULTATION_SELECT_TIME, callback_data=callback_data))
                session.close()
                
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_SELECT_TIME_1, reply_markup=markup)
            else:
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                for row in get_keyboard_row_list(ConsultationCommand.__get_answers(2), 2):
                    markup.row(*row)
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_STAGE_5, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=4)
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
