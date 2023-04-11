import telebot, datetime
import botsys.core.strcontent as strcontent
from botsys.core.system import get_keyboard_row_list, escape_markdownv2_text
from botsys.core.bot import Bot, InlineKeyboardDataBuilder
from botsys.db.model import User, Consultation, СonsultationAppointmentTime, Admin, ConsultationNotification
from sqlalchemy.orm.session import Session


class RegistrationCommand:
    @staticmethod
    def start_message_command(bot: Bot, message: telebot.types.Message, session: Session):
        user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()

        if user is None:
            bot.send_message(message.chat.id, strcontent.MESSAGE_START, parse_mode="MarkdownV2")
            bot.register_next_step_action(message.chat.id, message.from_user.id, RegistrationCommand.registation, stage=1, reg_data={})
        else:
            # Сообщение о том, что пользователь уже прошел регистрацию
            bot.send_message(message.chat.id, strcontent.MESSAGE_ALREADY_REGISTERED)

    @staticmethod
    def registation(bot: Bot, message: telebot.types.Message, session: Session, stage, reg_data):
        user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()

        if user is not None:
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

            bot.send_message(message.chat.id, strcontent.MESSAGE_REGISTRATION_SELECT_TIMEZONE.format(first_name=reg_data['first_name']), parse_mode="MarkdownV2", reply_markup=markup)
            bot.register_next_step_action(message.chat.id, message.from_user.id, RegistrationCommand.registation, stage=2, reg_data=reg_data)
        elif stage == 2:
            timezone = 3
            if message.text == strcontent.BUTTON_TIMEZONE_MSC_M1:
                timezone = 2
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P1:
                timezone = 4
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P2:
                timezone = 5
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P3:
                timezone = 6
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P4:
                timezone = 7
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P5:
                timezone = 8
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P6:
                timezone = 9
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P7:
                timezone = 10
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P8:
                timezone = 11
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC_P9:
                timezone = 12
            elif message.text == strcontent.BUTTON_TIMEZONE_MSC:
                pass
            else:
                bot.send_message(message.chat.id, strcontent.MESSAGE_REGISTRATION_SELECT_TIMEZONE.format(first_name=reg_data['first_name']), parse_mode="MarkdownV2")
                bot.register_next_step_action(message.chat.id, message.from_user.id, RegistrationCommand.registation, stage=2, reg_data=reg_data)
                return
            
            user = User(message.from_user.id)
            user.first_name = reg_data['first_name']
            user.tz_utc_offset = timezone
            session.add(user)
            session.commit()
            
            inline_markup = telebot.types.InlineKeyboardMarkup()
            keyboard_data_builder = InlineKeyboardDataBuilder(session)
            callback_data = keyboard_data_builder.build_single_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_CONSULTATION)
            inline_markup.add(telebot.types.InlineKeyboardButton(text=strcontent.BUTTON_CONSULTATION, callback_data=callback_data))

            markup = telebot.types.ReplyKeyboardRemove()

            # Экранирование спецсимволов MarkdownV2
            timezone_text = message.text.replace("+", "\\+").replace("-", "\\-")

            bot.send_message(message.chat.id, strcontent.MESSAGE_REGISTRATION_FINAL.format(first_name=reg_data['first_name'], timezone=timezone_text), parse_mode="MarkdownV2", reply_markup=markup)
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
    def message_command(bot: Bot, message: telebot.types.Message, session: Session):
        user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()

        if user is None:
            bot.send_message(message.chat.id, strcontent.MESSAGE_NEED_REGISTRATION)
            return

        markup = MenuCommand.__get_menu_markup(bot, session, user)
        text = MenuCommand.__get_menu_text()

        bot.send_message(message.chat.id, text, reply_markup=markup)

    @staticmethod
    def callback_query_command(bot: Bot, call: telebot.types.CallbackQuery, session: Session, callback_data: dict):
        user = session.query(User).filter_by(tg_user_id=call.from_user.id).first()

        if user is None:
            bot.answer_callback_query(call.id, strcontent.MESSAGE_NEED_REGISTRATION, show_alert=True)
            return
        
        action = callback_data.get("action", 0)
        if action == -1:
            text = strcontent.MESSAGE_MENU_CLOSED
            bot.edit_message_text(text, call.message.chat.id, call.message.id)
        elif action == 0:
            markup = MenuCommand.__get_menu_markup(bot, session, user)
            text = MenuCommand.__get_menu_text()
            bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, strcontent.NOTIFICATION_UNKNOWN_COMMAND)

    @staticmethod
    def __get_menu_markup(bot: Bot, session: Session, user: User) -> telebot.types.InlineKeyboardButton:
        markup = telebot.types.InlineKeyboardMarkup()
        keyboard_data_builder = InlineKeyboardDataBuilder(session)
        buttons = []

        if user.role is None:
            keyboard_data_builder.add_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_CONSULTATION)
            buttons.append(strcontent.BUTTON_CONSULTATION)
        elif (user.role is not None) and (user.role.is_admin()):
            keyboard_data_builder.add_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_ADMIN_PANEL)
            buttons.append(strcontent.BUTTON_ADMIN_PANEL)

        buttons.append(strcontent.BUTTON_CLOSE)
        keyboard_data_builder.add_callback_data(command=strcontent.COMMAND_MESSAGE_MENU, action=-1)

        button_ids = keyboard_data_builder.build()

        for i in range(len(buttons)):
            markup.add(telebot.types.InlineKeyboardButton(buttons[i], callback_data=button_ids[i]))
        
        return markup

    @staticmethod
    def __get_menu_text() -> str:
        return strcontent.MESSAGE_MENU


class ConsultationCommand:
    @staticmethod
    def callback_query_command(bot: Bot, call: telebot.types.CallbackQuery, session: Session, callback_data: dict):
        user = session.query(User).filter_by(tg_user_id=call.from_user.id).first()

        if user is None:
            bot.answer_callback_query(call.id, strcontent.NOTIFICATION_NEED_REGISTRATION)
            return
        
        action = callback_data.get("action", 1)
        if action == -1:
            bot.edit_message_text(strcontent.MESSAGE_CONSULTATION_CANCELED, call.message.chat.id, call.message.id)
        elif action == 1:
            if user.consultations.filter_by(is_processed=False).first() is not None:
                bot.answer_callback_query(call.id, strcontent.NOTIFICATION_YOU_HAVE_ALREADY_ACTIVE_CONSULTATION, show_alert=True)
                return
            elif user.role is not None:
                bot.answer_callback_query(call.id, strcontent.NOTIFICATION_YOU_HAVE_NO_ACCESS)
                return

            stage = callback_data.get("stage", 1)
            form = callback_data.get("form", {})
            if stage == 1:
                inline_markup = telebot.types.InlineKeyboardMarkup()
                bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=inline_markup)

                markup = telebot.types.ReplyKeyboardRemove()
                text = f"{strcontent.MESSAGE_CONSULTATION_START}\n\n{strcontent.MESSAGE_CONSULTATION_TELL_AGE}"
                bot.send_message(call.message.chat.id, text, reply_markup=markup)
                bot.register_next_step_action(call.message.chat.id, call.from_user.id, ConsultationCommand.get_age, form=form)
            elif stage == 2:
                tz_timedelta = datetime.timedelta(hours=user.tz_utc_offset)

                utc_time = datetime.datetime.utcnow()
                user_time = utc_time + tz_timedelta
                interval = datetime.timedelta(days=1)

                callback_data_builder = InlineKeyboardDataBuilder(session)
                button_text = []

                for i in range(7):
                    user_time = user_time + interval

                    callback_data = {
                        "command": callback_data["command"],
                        "action": 1,
                        "stage": 3,
                        "form": callback_data["form"],
                        "time": {"day": user_time.day, "month": user_time.month, "year": user_time.year}
                    }
                    callback_data_builder.add_callback_data(**callback_data)

                    date_text = f"0{user_time.day}" if user_time.day < 10 else f"{user_time.day}"
                    date_text = f"{date_text}.0{user_time.month}" if user_time.month < 10 else f"{date_text}.{user_time.month}"
                    button_text.append(date_text)
                callback_data_builder.add_callback_data(command=callback_data["command"], action=-1)
                button_ids = callback_data_builder.build()

                buttons = []
                for i in range(len(button_text)):
                    buttons.append(telebot.types.InlineKeyboardButton(button_text[i], callback_data=button_ids[i]))

                markup = telebot.types.InlineKeyboardMarkup()
                for row in get_keyboard_row_list(buttons):
                    markup.row(*row)
                #markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_CANCEL, callback_data=button_ids[-1]))

                bot.edit_message_text(strcontent.MESSAGE_CONSULTATION_SELECT_DATE, call.message.chat.id, call.message.id, reply_markup=markup)
            elif stage == 3:
                tz_utc_offset = user.tz_utc_offset
                tz_timedelta = datetime.timedelta(hours=tz_utc_offset)

                utc_time = datetime.datetime.utcnow()

                date_day = callback_data["time"]["day"]
                date_month = callback_data["time"]["month"]
                date_year = callback_data["time"]["year"]
                date_text = f"0{date_day}" if date_day < 10 else f"{date_day}"
                date_text = f"{date_text}\\.0{date_month}" if date_month < 10 else f"{date_text}\\.{date_month}"

                callback_data_builder = InlineKeyboardDataBuilder(session)
                button_text = []
                appointment_times_utc = session.query(СonsultationAppointmentTime).order_by(СonsultationAppointmentTime.utc_hour, СonsultationAppointmentTime.utc_minute).all()

                appointment_times = []
                for time in appointment_times_utc:
                    msc_hour = time.utc_hour + tz_utc_offset
                    if msc_hour > 23:
                        msc_hour = msc_hour - 24
                    appointment_times.append([msc_hour, time.utc_minute])

                # Сортируем время по возврастанию
                for i in range(len(appointment_times)):
                    for j in range(i, len(appointment_times)):
                        if (appointment_times[i][0] > appointment_times[j][0]) or ((appointment_times[i][0] == appointment_times[j][0]) and (appointment_times[i][1] > appointment_times[j][1])):
                            tmp = appointment_times[i]
                            appointment_times[i] = appointment_times[j]
                            appointment_times[j] = tmp

                

                for appointment_time in appointment_times:
                    display_hour = appointment_time[0]
                    display_minute = appointment_time[1]

                    user_utc_time = datetime.datetime(
                        year=date_year, month=date_month, day=date_day,
                        hour=display_hour, minute=display_minute
                    )
                    user_utc_time = user_utc_time - tz_timedelta

                    if user_utc_time > utc_time:
                        time_text = f"0{display_hour}" if display_hour < 10 else f"{display_hour}"
                        time_text = f"{time_text}:0{display_minute}" if display_minute < 10 else f"{time_text}:{display_minute}"
                        button_text.append(time_text)

                        callback_data = {
                            "command": callback_data["command"],
                            "action": 1,
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

                callback_data_builder.add_callback_data(command=callback_data["command"], action=1, stage=2, form=callback_data["form"])  
                #callback_data_builder.add_callback_data(command=callback_data["command"], stage=-1)
                button_ids = callback_data_builder.build()

                buttons = []
                for i in range(len(button_text)):
                    buttons.append(telebot.types.InlineKeyboardButton(button_text[i], callback_data=button_ids[i]))

                markup = telebot.types.InlineKeyboardMarkup()
                for row in get_keyboard_row_list(buttons):
                    markup.row(*row)
                #markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_CANCEL, callback_data=button_ids[-1]))
                markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_BACK, callback_data=button_ids[-1]))

                bot.edit_message_text(strcontent.MESSAGE_CONSULTATION_SELECT_TIME.format(date=date_text), call.message.chat.id, call.message.id, reply_markup=markup, parse_mode="MarkdownV2")
            elif stage == 4:
                tz_timedelta = datetime.timedelta(hours=user.tz_utc_offset)

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

                callback_data_builder = InlineKeyboardDataBuilder(session)
                callback_data_builder.add_callback_data(
                    command=callback_data["command"], action=1, stage=5,
                    form=callback_data["form"], time=callback_data["time"]
                )
                callback_data_builder.add_callback_data(
                    command=callback_data["command"], action=1, stage=2,
                    form=callback_data["form"]
                )
                callback_data_builder.add_callback_data(command=callback_data["command"], action=-1)
                button_ids = callback_data_builder.build()

                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_CONFIRM, callback_data=button_ids[0]))
                markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_CONSULTATION_CHANGE_TIME, callback_data=button_ids[1]))
                markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_CANCEL, callback_data=button_ids[2]))

                embedded_text_list = {'date': date_text, 'time': time_text, 'user_name': user.get_full_name()}
                embedded_text_list = {**embedded_text_list, **callback_data["form"]}
                for i in embedded_text_list:
                    if(isinstance(embedded_text_list[i], str)):
                        embedded_text_list[i] = escape_markdownv2_text(embedded_text_list[i])

                text = strcontent.MESSAGE_CONSULTATION_CONFIRMATION.format(**embedded_text_list)
                bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup, parse_mode="MarkdownV2")
            elif stage == 5:
                consultation_time = datetime.datetime(
                    year=callback_data["time"]["year"], month=callback_data["time"]["month"],
                    day=callback_data["time"]["day"], hour=callback_data["time"]["hour"],
                    minute=callback_data["time"]["minute"], second=0, microsecond=0
                )
                consultation = Consultation(
                    user.user_id, callback_data["form"]["age"], callback_data["form"]["phone_number"],
                    callback_data["form"]["lang_level"], callback_data["form"]["hsk_exam"],
                    callback_data["form"]["purpose"], callback_data["form"]["way_now"], consultation_time
                )

                session.add(consultation)
                session.commit()

                text = strcontent.MESSAGE_CONSULTATION_SENT.format(consultation_id=consultation.consultation_id)
                bot.edit_message_text(text, call.message.chat.id, call.message.id)
                
                # Уведомление администратора консультаций
                notification_admin = session.query(Admin).filter_by(is_consultation_admin=True).first()
                if notification_admin is not None:
                    user_admin = notification_admin.role.user
                    
                    markup = telebot.types.InlineKeyboardMarkup()
                    callback_data_builder = InlineKeyboardDataBuilder(session)
                    callback_data = callback_data_builder.build_single_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_CONSULTATION, action=2, consultation_id=consultation.consultation_id)
                    markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_CONSULTATION_MARK_AS_PROCESSED, callback_data=callback_data))

                    notification_text = ConsultationCommand.__get_notifiction_text(user_admin, consultation)
                    notification_message = bot.send_message(user_admin.tg_user_id, notification_text, reply_markup=markup, parse_mode="MarkdownV2")
                    notification = ConsultationNotification(
                        consultation.consultation_id, notification_message.chat.id, notification_message.id
                    )
                    session.add(notification)
                    session.commit()
        elif action == 2:
            if (user.role is None) or not (user.role.is_admin()):
                bot.answer_callback_query(call.id, strcontent.NOTIFICATION_YOU_HAVE_NO_ACCESS)
                return
            
            consultation = session.query(Consultation).filter_by(consultation_id=callback_data["consultation_id"]).first()
            if consultation is None:
                text = strcontent.MESSAGE_CONSULTATION_UNKNOWN.format(consultation_id=callback_data["consultation_id"])
                bot.edit_message_text(text, call.message.chat.id, call.message.id)
                return
            
            subaction = callback_data.get("subaction", 1)
            if subaction == 1:
                markup = telebot.types.InlineKeyboardMarkup()
                buttons = [
                    strcontent.BUTTON_CONFIRM,
                    strcontent.BUTTON_BACK
                ]
                callback_data_builder = InlineKeyboardDataBuilder(session)
                callback_data_builder.add_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_CONSULTATION, action=2, subaction=3, consultation_id=callback_data["consultation_id"])
                callback_data_builder.add_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_CONSULTATION, action=2, subaction=2, consultation_id=callback_data["consultation_id"])
                button_ids = callback_data_builder.build()
                for i in range(len(buttons)):
                    markup.add(telebot.types.InlineKeyboardButton(buttons[i], callback_data=button_ids[i]))
                text = ConsultationCommand.__get_notifiction_text(user, consultation)

                text = f"{text}\n\n{strcontent.MESSAGE_CONSULTATION_SYSTEM_MSG}\n{strcontent.MESSAGE_CONSULTATION_QUESTION_MARK_AS_PROCESSED}"
                bot.edit_message_text(text, call.message.chat.id, call.message.id, parse_mode="MarkdownV2", reply_markup=markup)
            elif subaction == 2:
                markup = telebot.types.InlineKeyboardMarkup()
                callback_data_builder = InlineKeyboardDataBuilder(session)
                callback_data = callback_data_builder.build_single_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_CONSULTATION, action=2, consultation_id=consultation.consultation_id)
                markup.add(telebot.types.InlineKeyboardButton(strcontent.BUTTON_CONSULTATION_MARK_AS_PROCESSED, callback_data=callback_data))
                text = ConsultationCommand.__get_notifiction_text(user, consultation)
                bot.edit_message_text(text, call.message.chat.id, call.message.id, parse_mode="MarkdownV2", reply_markup=markup)
            elif subaction == 3:
                consultation.is_processed = True
                session.commit()

                text = ConsultationCommand.__get_notifiction_text(user, consultation)
                bot.edit_message_text(text, call.message.chat.id, call.message.id, parse_mode="MarkdownV2")
            else:
                bot.answer_callback_query(call.id, strcontent.NOTIFICATION_UNKNOWN_COMMAND)
        else:
            bot.answer_callback_query(call.id, strcontent.NOTIFICATION_UNKNOWN_COMMAND)

    @staticmethod
    def get_age(bot: Bot, message: telebot.types.Message, session: Session, form):
        user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()

        if user is None:
            bot.send_message(message.chat.id, strcontent.MESSAGE_NEED_REGISTRATION)
            return
        
        if message.content_type == 'text':
            age = 0
            try:
                age = int(message.text)
            except ValueError:
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TELL_AGE)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_age, form=form)
                return
            
            if (1 <= age) and (age <= 99):
                form['age'] = age
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CONSULTATION_TG_PHONE_NUMBER, request_contact=True))
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TELL_PHONE_NUMBER, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_phone_number, form=form)
            else:
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TELL_AGE)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_age, form=form)
        else:
            bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TELL_AGE)
            bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_age, form=form)
    @staticmethod
    def get_phone_number(bot: Bot, message: telebot.types.Message, session: Session, form):
        user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()

        if user is None:
            bot.send_message(message.chat.id, strcontent.MESSAGE_NEED_REGISTRATION)
            return

        if message.content_type == 'contact':
            form["phone_number"] = message.contact.phone_number
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            for row in get_keyboard_row_list(ConsultationCommand.__get_answers(1)):
                markup.row(*row)
            bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_Q_LANG_LEVEL, reply_markup=markup)
            bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=1)
        elif message.content_type == 'text':
            if message.text == strcontent.BUTTON_CANCEL:
                markup = telebot.types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_CANCELED, reply_markup=markup)
            else:
                if len(message.text) == 10 and ConsultationCommand.__validate_phone_number(message.text):
                    form["phone_number"] = f"7{message.text}"
                    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                    for row in get_keyboard_row_list(ConsultationCommand.__get_answers(1)):
                        markup.row(*row)
                    bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_Q_LANG_LEVEL, reply_markup=markup)
                    bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=1)
                else:
                    bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TELL_PHONE_NUMBER)
                    bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_phone_number, form=form)
        else:
            bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TELL_PHONE_NUMBER)
            bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_phone_number, form=form)

    @staticmethod
    def get_answers_to_survey(bot: Bot, message: telebot.types.Message, session: Session, form, q):
        user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()

        if user is None:
            bot.send_message(message.chat.id, strcontent.MESSAGE_NEED_REGISTRATION)
            return
        
        if message.text == strcontent.BUTTON_CANCEL:
            markup = telebot.types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_CANCELED, reply_markup=markup)
        elif q == 1:
            if message.text in ConsultationCommand.__get_answers(1):
                form["lang_level"] = message.text
                markup = telebot.types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_Q_HSK_EXAM, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=2)
            else:
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                for row in get_keyboard_row_list(ConsultationCommand.__get_answers(1)):
                    markup.row(*row)
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_Q_LANG_LEVEL, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=1)
        elif q == 2:
            if len(message.text) <= 100:
                form['hsk_exam'] = message.text
                markup = telebot.types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_Q_PURPOSE, reply_markup=markup)
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
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_Q_WAY_NOW, reply_markup=markup)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=4)
            else:
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_TOO_LONG_ANSWER)
                bot.register_next_step_action(message.chat.id, message.from_user.id, ConsultationCommand.get_answers_to_survey, form=form, q=3)
        elif q == 4:
            if message.text in ConsultationCommand.__get_answers(2):
                form['way_now'] = message.text
                markup = telebot.types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_Q_SELECT_TIME, reply_markup=markup)
                markup = telebot.types.InlineKeyboardMarkup()
                keyboard_data_builder = InlineKeyboardDataBuilder(session)
                callback_data = keyboard_data_builder.build_single_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_CONSULTATION, action=1, stage=2, form=form)
                markup.add(telebot.types.InlineKeyboardButton(text=strcontent.BUTTON_CONSULTATION_SELECT_TIME, callback_data=callback_data))
                
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_MENU_SELECT_TIME, reply_markup=markup)
            else:
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                for row in get_keyboard_row_list(ConsultationCommand.__get_answers(2), 2):
                    markup.row(*row)
                bot.send_message(message.chat.id, strcontent.MESSAGE_CONSULTATION_Q_WAY_NOW, reply_markup=markup)
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
        
    def __get_notifiction_text(user_admin: User, consultation: Consultation):
        tz_timedelta = datetime.timedelta(hours=user_admin.tz_utc_offset)

        user = consultation.user

        creation_time = consultation.creation_time + tz_timedelta
        consultation_time = consultation.consultation_time + tz_timedelta
        consultation_status = strcontent.MESSAGE_CONSULTATION_STATUS_PROCESSED if consultation.is_processed else strcontent.MESSAGE_CONSULTATION_STATUS_NOT_PROCESSED

        embedded_text_list = {
            'consultation_id': consultation.consultation_id,
            'creation_time': creation_time.strftime("%d.%m.%y %H:%M"),
            'consultation_status': consultation_status,
            'user_fullname': user.get_full_name(middle_name=False),
            'age': consultation.age,
            'user_id': user.user_id,
            'consultation_time': consultation_time.strftime("%d.%m.%y %H:%M"),
            'user_phone_number': f"+{consultation.phone_number}",
            'tg_user_id': user.tg_user_id,
            'lang_level': consultation.lang_level,
            'hsk_exam': consultation.hsk_exam,
            'purpose': consultation.purpose,
            'way_now': consultation.way_now
        }
        for i in embedded_text_list:
            if isinstance(embedded_text_list[i], str):
                embedded_text_list[i] = escape_markdownv2_text(embedded_text_list[i])

        return strcontent.MESSAGE_CONSULTATION_NOTIFICATION.format(**embedded_text_list)
        

class AdminPanel:
    @staticmethod
    def callback_query_command(bot: Bot, call: telebot.types.CallbackQuery, session: Session, callback_data: dict):
        user = session.query(User).filter_by(tg_user_id=call.from_user.id).first()

        if user is None:
            bot.answer_callback_query(call.id, strcontent.NOTIFICATION_NEED_REGISTRATION)
            return
        elif (user.role is None) or not (user.role.is_admin()):
            bot.answer_callback_query(call.id, strcontent.NOTIFICATION_YOU_HAVE_NO_ACCESS)
            return
        
        action = callback_data.get("action", 0)

        if action == 1:
            subaction = callback_data.get("subaction", 0)

            if subaction == 1:
                markup = telebot.types.InlineKeyboardMarkup()
                bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=markup)
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CLOSE))
                bot.send_message(call.message.chat.id, strcontent.MESSAGE_ADMIN_PANEL_ENTER_CONSULTATION_APPOINTMENT_TIMES, reply_markup=markup)
                bot.register_next_step_action(call.message.chat.id, call.from_user.id, AdminPanel.get_appointment_time)
            else:
                appointment_times = session.query(СonsultationAppointmentTime).order_by(СonsultationAppointmentTime.utc_hour, СonsultationAppointmentTime.utc_minute).all()

                # Получаем двухмерный массив времени в МСК
                appointment_times_msc = []
                for time in appointment_times:
                    msc_hour = time.utc_hour + 3
                    if msc_hour > 23:
                        msc_hour = msc_hour - 24
                    appointment_times_msc.append([msc_hour, time.utc_minute])

                # Сортируем время по возврастанию
                for i in range(len(appointment_times_msc)):
                    for j in range(i, len(appointment_times_msc)):
                        if (appointment_times_msc[i][0] > appointment_times_msc[j][0]) or ((appointment_times_msc[i][0] == appointment_times_msc[j][0]) and (appointment_times_msc[i][1] > appointment_times_msc[j][1])):
                            tmp = appointment_times_msc[i]
                            appointment_times_msc[i] = appointment_times_msc[j]
                            appointment_times_msc[j] = tmp

                appointment_times_text = ""
                for i in appointment_times_msc:
                    hour = i[0]
                    minute = i[1]
                    hour_text = f"0{hour}" if hour < 10 else str(hour)
                    minute_text = f"0{minute}" if minute < 10 else str(minute)
                    appointment_times_text = f"{hour_text}:{minute_text}" if appointment_times_text == "" else f"{appointment_times_text} {hour_text}:{minute_text}"

                text = strcontent.MESSAGE_ADMIN_PANEL_CONSULTATION_APPOINTMENT_TIMES
                text = f"{text}\n{appointment_times_text}"

                markup = telebot.types.InlineKeyboardMarkup()
                keyboard_data_builder = InlineKeyboardDataBuilder(session)

                buttons = [
                    strcontent.BUTTON_ADMIN_PANEL_CHANGE_CONSULTATION_APPOINTMENT_TIMES,
                    strcontent.BUTTON_BACK
                ]

                keyboard_data_builder.add_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_ADMIN_PANEL, action=1, subaction=1)
                keyboard_data_builder.add_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_ADMIN_PANEL)

                button_ids = keyboard_data_builder.build()
                for i in range(len(buttons)):
                    markup.add(telebot.types.InlineKeyboardButton(buttons[i], callback_data=button_ids[i]))

                bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup)
        else:
            markup = telebot.types.InlineKeyboardMarkup()
            keyboard_data_builder = InlineKeyboardDataBuilder(session)
            message_text = strcontent.MESSAGE_ADMIN_PANEL

            if action == 10:
                notification_admin = session.query(Admin).filter_by(is_consultation_admin=True).first()
                if notification_admin is None or (notification_admin.user_role_id == user.role.user_role_id):
                    user.role.admin.is_consultation_admin = not user.role.admin.is_consultation_admin
                else:
                    notification_admin.is_consultation_admin = False
                    user.role.admin.is_consultation_admin = True

                    # Уведомляем предыдущего админа о преостановке уведомлений
                    admin_tg_user_id = notification_admin.role.user.tg_user_id
                    bot.send_message(admin_tg_user_id, strcontent.MESSAGE_CONSULTATION_NOTIFICATION_OFF)
                result = strcontent.MESSAGE_CONSULTATION_NOTIFICATION_ON if user.role.admin.is_consultation_admin else strcontent.MESSAGE_CONSULTATION_NOTIFICATION_OFF
                message_text = f"{message_text}\n\n{result}"
                session.commit()

            notification_button_text = strcontent.BUTTON_ADMIN_PANEL_CONSULTATION_NOTIFICATION_OFF
            if user.role.admin.is_consultation_admin:
                notification_button_text = strcontent.BUTTON_ADMIN_PANEL_CONSULTATION_NOTIFICATION_ON

            buttons = [
                strcontent.BUTTON_ADMIN_PANEL_CONSULTATION_TIME,
                notification_button_text,
                strcontent.BUTTON_BACK
            ]

            keyboard_data_builder.add_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_ADMIN_PANEL, action=1)
            keyboard_data_builder.add_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_ADMIN_PANEL, action=10)
            keyboard_data_builder.add_callback_data(command=strcontent.COMMAND_CALLBACK_QUERY_MENU)

            button_ids = keyboard_data_builder.build()
            for i in range(len(buttons)):
                markup.add(telebot.types.InlineKeyboardButton(buttons[i], callback_data=button_ids[i]))

            bot.edit_message_text(message_text, call.message.chat.id, call.message.id, reply_markup=markup)

    @staticmethod
    def get_appointment_time(bot: Bot, message: telebot.types.Message, session: Session):
        user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()

        if user is None:
            bot.send_message(message.chat.id, strcontent.MESSAGE_NEED_REGISTRATION)
            return
        
        if message.text == strcontent.BUTTON_CLOSE:
            markup = telebot.types.ReplyKeyboardRemove()
            text = strcontent.MESSAGE_ADMIN_PANEL_ENTER_CONSULTATION_APPOINTMENT_TIMES_CLOSED
            bot.send_message(message.chat.id, text, reply_markup=markup)
        else:
            appointment_times = []

            # Парсинг времени
            for msc_time_text in message.text.split():
                msc_time_text_splitted = msc_time_text.split(":")

                try:
                    hour = int(msc_time_text_splitted[0])
                    minute = int(msc_time_text_splitted[1])

                    if (0 <= hour and hour <= 23) and (0 <= minute and minute <= 59):
                        appointment_times.append([hour, minute])
                except:
                    pass
            
            # Повторяем процедуру запроса времени если ни одно время не было спарсено
            if len(appointment_times) == 0:
                bot.send_message(message.chat.id, strcontent.MESSAGE_ADMIN_PANEL_ENTER_CONSULTATION_APPOINTMENT_TIMES)
                bot.register_next_step_action(message.chat.id, message.from_user.id, AdminPanel.get_appointment_time)
                return
            
            # Сортируем время по возврастанию
            for i in range(len(appointment_times)):
                for j in range(i, len(appointment_times)):
                    if (appointment_times[i][0] > appointment_times[j][0]) or ((appointment_times[i][0] == appointment_times[j][0]) and (appointment_times[i][1] > appointment_times[j][1])):
                        tmp = appointment_times[i]
                        appointment_times[i] = appointment_times[j]
                        appointment_times[j] = tmp
            
            # Формируем строку из времен
            appointment_times_text = ""
            for i in appointment_times:
                hour = i[0]
                minute = i[1]
                hour_text = f"0{hour}" if hour < 10 else str(hour)
                minute_text = f"0{minute}" if minute < 10 else str(minute)
                appointment_times_text = f"{hour_text}:{minute_text}" if appointment_times_text == "" else f"{appointment_times_text} {hour_text}:{minute_text}"

            # Преобразуем время в UTC
            for i in range(len(appointment_times)):
                appointment_times[i][0] -= 3
                if appointment_times[i][0] < 0:
                    appointment_times[i][0] += 24

            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CONFIRM))
            markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
            
            text = strcontent.MESSAGE_ADMIN_PANEL_CONSULTATION_APPOINTMENT_CHANGING_INFO.format(appointment_times=appointment_times_text)
            bot.send_message(message.chat.id, text, reply_markup=markup)
            bot.register_next_step_action(message.chat.id, message.from_user.id, AdminPanel.set_appointment_time, appointment_times=appointment_times)

    @staticmethod
    def set_appointment_time(bot: Bot, message: telebot.types.Message, session: Session, appointment_times):
        user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()

        if user is None:
            bot.send_message(message.chat.id, strcontent.MESSAGE_NEED_REGISTRATION)
            return
        
        if message.text == strcontent.BUTTON_CONFIRM:
            session.query(СonsultationAppointmentTime).delete()
            for i in appointment_times:
                cat = СonsultationAppointmentTime(i[0], i[1])
                session.add(cat)
            session.commit()

            markup = telebot.types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, strcontent.MESSAGE_ADMIN_PANEL_CONSULTATION_APPOINTMENT_CHANGED, reply_markup=markup)
        elif message.text == strcontent.BUTTON_CANCEL:
            markup = telebot.types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, strcontent.MESSAGE_ADMIN_PANEL_ENTER_CONSULTATION_APPOINTMENT_TIMES_CLOSED, reply_markup=markup)
        else:
            # Преобразуем время в MSC
            appointment_times_msc = []
            for i in range(len(appointment_times)):
                appointment_times_msc.append([0, 0])
                appointment_times_msc[-1][0] = appointment_times[i][0] + 3
                appointment_times_msc[-1][1] = appointment_times[i][1]
                if appointment_times_msc[-1][0] > 23:
                    appointment_times_msc[-1][0] -= 24

            # Формируем строку из времен
            appointment_times_msc_text = ""
            for i in appointment_times_msc:
                hour = i[0]
                minute = i[1]
                hour_text = f"0{hour}" if hour < 10 else str(hour)
                minute_text = f"0{minute}" if minute < 10 else str(minute)
                appointment_times_msc_text = f"{hour_text}:{minute_text}" if appointment_times_msc_text == "" else f"{appointment_times_msc_text} {hour_text}:{minute_text}"

            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CONFIRM))
            markup.add(telebot.types.KeyboardButton(strcontent.BUTTON_CANCEL))
            text = strcontent.MESSAGE_ADMIN_PANEL_CONSULTATION_APPOINTMENT_CHANGING_INFO.format(appointment_times=appointment_times_msc_text)
            bot.send_message(message.chat.id, text, reply_markup=markup)
            bot.register_next_step_action(message.chat.id, message.from_user.id, AdminPanel.set_appointment_time, appointment_times=appointment_times)
        

