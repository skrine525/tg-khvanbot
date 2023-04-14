# Модуль, содержащий все строковые константы, используемые в боте


MESSAGE_CONTENT_NOT_AVAILABLE = "⛔️ Содержимое недоступно."
MESSAGE_COMMANDS_NOT_AVAILABLE_TO_ANONYMOUS_IN_GROUP = "⛔️ Команды недоступны для анонимных в группе пользователей."
MESSAGE_UNKNOWN_USER = "К сожалению, мы вас не знаем. Нажмите на /start и пройдите регистраци."
MESSAGE_ALREADY_REGISTERED = "Вы уже зарегистрированы."
MESSAGE_NEED_REGISTRATION = "⛔️ Для начала необходимо зарегистрироваться.\nНажмите на /start для прохождения регистрации."
MESSAGE_START = "你好👋\n\nНа связи школа китайского языка «Хван»🇨🇳\nС любовью преподаем китайский❤️\n\nДавайте познакомимся🤗\n📝 Напишите свое *имя*\\."
MESSAGE_REGISTRATION_TOO_LONG_FIRST_NAME = "Введеное имя слишком длинное.\nУкажите короткую форму имени."
MESSAGE_REGISTRATION_PROHIBITED_SYMBOLS_CANNOT_BE_USED = "⛔️ Используйте __только__ буквы *русского* и *английского* алфавитов\\."
MESSAGE_REGISTRATION_SELECT_TIMEZONE = "Здравствуйте, {first_name}\\. Приятно с вами познакомиться\\.\n\n🔘 Выберите свой *часовой пояс*\\."
MESSAGE_REGISTRATION_FINAL = "1️⃣ *Имя*: {first_name}\n2️⃣ *Часовой пояс*: {timezone}\n\n✅ Регистрация пройдена\\."
MESSAGE_OFFER_CONSULTATION = "📞 Теперь вы можете записаться на консультацию."
MESSAGE_CONSULTATION_START = "Отлично! Давайте запишем вас на консультацию."
MESSAGE_CONSULTATION_TELL_AGE = "🧬 Укажите возраст (1-99) человека, который будет заниматься в школе."
MESSAGE_CONSULTATION_Q_LANG_LEVEL = "Теперь необходимо ответить на несколько вопросов.\n\nКакой у вас уровень китайского языка?\n• HSK 1 (примерно 150 иероглифов)\n• HSK 2 (примерно 300 иероглифов)\n• HSK 3 (примерно 600 иероглифов)\n• HSK 4 (примерно 1200 иероглифов)\n• HSK 5 (примерно 2500 иероглифов)\n• HSK 6 😎\n• Нулевой (еще не начинал(а) изучать)\n• Не знаю"
MESSAGE_CONSULTATION_Q_HSK_EXAM = "Планируете сдавать экзамен HSK? (Если да, то когда и какой уровень хотели бы сдать?).\n\nНапишите письменный ответ."
MESSAGE_CONSULTATION_Q_PURPOSE = "Какая цель на китайский язык сейчас?\n\nНапишите письменный ответ."
MESSAGE_CONSULTATION_Q_WAY_NOW = "Как Вы сейчас изучаете язык?\n• Никак\n• Онлайн-курсы\n• Онлайн с репетитором\n• Встречаюсь с репетитором (очно)\n• Хожу на групповые занятия\n• Самостоятельно (смотрю ютуб, дорамы, решаю тесты и др.)"
MESSAGE_CONSULTATION_Q_SELECT_TIME = "✅ Анкета заполнена. Теперь выберите удобное время консультации."
MESSAGE_CONSULTATION_CANCELED = "✅ Создание заявки на консультацию отменено."
MESSAGE_CONSULTATION_TELL_PHONE_NUMBER = "Укажите номер телефона. Вы можете:\n1️⃣ Предоставить номер Telegram\n2️⃣ Указать другой номер без кода +7."
MESSAGE_CONSULTATION_CREATION_ERROR = "⛔️ Произошла ошибка. Попробуйте еще раз записаться на консультацию."
MESSAGE_CONSULTATION_TOO_LONG_ANSWER = "⛔️ Ответ содержит более 100 символов. Пожалуйста, напишите ответ короче."
MESSAGE_CONSULTATION_MENU_SELECT_TIME = "🗓 Выберите удобное время консультации."
MESSAGE_CONSULTATION_SELECT_DATE = "🗓 Выберите дату."
MESSAGE_CONSULTATION_SELECT_TIME = "📅 *Дата*: {date}\n\n🗓 Выберите время\\."
MESSAGE_CONSULTATION_CONFIRMATION = "👤 *Имя*: {user_name}\n🧬 *Возраст*: {age}\n☎️ *Телефон*: {phone_number}\n📅 *Дата*: {date}\n⏰ *Время*: {time}\n\n*В*: Какой у вас уровень китайского языка?\n*О*: {lang_level}\n\n*В*: Планируете сдавать экзамен HSK? \\(Если да, то когда и какой уровень хотели бы сдать?\\)\n*О*: {hsk_exam}\n\n*В*: Какая цель на китайский язык сейчас?\n*О*: {purpose}\n\n*В*: Как Вы сейчас изучаете язык?\n*О*: {way_now}"
MESSAGE_CONSULTATION_SENT = "✅ Заявка на консультацию отправлена.\n🆔 Номер заявки: {consultation_id}"
MESSAGE_CONSULTATION_NOTIFICATION = "✉️ _Консультация №{consultation_id}_\n⌛️ *Время заявки*: {creation_time}\n🔘 *Статус*: {consultation_status}\n\n👤 *Имя*: {user_fullname}\n🆔 *ID*: {user_id}\n🧬 *Возраст*: {age}\n☎️ *Номер телефона*: {user_phone_number}\n💬 *Telegram*: [профиль](tg://user?id={tg_user_id})\n⏰ *Время консультации*: {consultation_time}\n\n*В*: Какой у вас уровень китайского языка?\n*О*: {lang_level}\n\n*В*: Планируете сдавать экзамен HSK? \\(Если да, то когда и какой уровень хотели бы сдать?\\)\n*О*: {hsk_exam}\n\n*В*: Какая цель на китайский язык сейчас?\n*О*: {purpose}\n\n*В*: Как Вы сейчас изучаете язык?\n*О*: {way_now}"
MESSAGE_CONSULTATION_NOTIFICATION_OFF = "❌ Вы больше не будете получать уведомления о консультациях."
MESSAGE_CONSULTATION_NOTIFICATION_ON = "✅ Теперь вы будете получать уведомления о консультациях."
MESSAGE_CONSULTATION_STATUS_PROCESSED = "✅ Выполнена"
MESSAGE_CONSULTATION_STATUS_NOT_PROCESSED = "❌ Не выполнена"
MESSAGE_CONSULTATION_SYSTEM_MSG = "⚙️ Сообщение от системы:"
MESSAGE_CONSULTATION_UNKNOWN = "⛔️ Консультации №{consultation_id} не существует."
MESSAGE_CONSULTATION_QUESTION_MARK_AS_PROCESSED = "Вы хотите пометить консультацию как *Выполнена*?"
MESSAGE_MENU = "📱 Главное меню."
MESSAGE_MENU_CLOSED = "📱 Главное меню закрыто."
MESSAGE_ADMIN_PANEL = "🧑‍💻 Админ-панель."
MESSAGE_ADMIN_PANEL_ENTER_CONSULTATION_APPOINTMENT_TIMES = "📅 Дата: {date}\n\n⏰ Укажите время приёма (по МСК) в формате ЧЧ:ММ, используя пробел, как разделитель.\n💬 Например: 10:00 10:30 12:25"
MESSAGE_ADMIN_PANEL_ENTER_CONSULTATION_APPOINTMENT_TIMES_CLOSED = "✅ Настройка приёма консультаций закрыта."
MESSAGE_ADMIN_PANEL_CONSULTATION_APPOINTMENT_INFO = "📅 Дата: {date}\n⏰ Время приёма (МСК): {appointment_times}"
MESSAGE_ADMIN_PANEL_CONSULTATION_APPOINTMENT_CHANGING_CONFIRMATION = "Все верно?"
MESSAGE_ADMIN_PANEL_CONSULTATION_APPOINTMENT_CHANGED = "✅ Время приёма консультаций обновлено."
MESSAGE_ADMIN_PANEL_CONSULTATION_APPOINTMENT_SELECT_DATE = "📅 Выберите дату (МСК), чтобы настроить время приёма консультаций."
MESSAGE_ADMIN_PANEL_CONSULTATION_APPOINTMENT_NOT_GIVEN = "❗️ Пусто"
MESSAGE_CONSULTATION_NOTIFICATION_APPOINTMENT_NOT_GIVEN = "❗️ Не указано"

NOTIFICATION_UNKNOWN_COMMAND = "⛔️ Неизвестная команда."
NOTIFICATION_YOU_DO_NOT_HAVE_ACCESS_TO_THIS_MENU = "⛔️ У вас нет доступа к этому меню."
NOTIFICATION_NEED_REGISTRATION = "⛔️ Для начала необходимо зарегистрироваться."
NOTIFICATION_YOU_HAVE_ALREADY_ACTIVE_CONSULTATION = "⛔️ Вы уже создали запрос на консультацию. С вами должны связаться в указанное время."
NOTIFICATION_YOU_HAVE_NO_ACCESS = "⛔️ У вас нет доступа к этой операции."
NOTIFICATION_CONSULTATION_APPOINTMENT_NO_LONGER_AVAILABLE = "⛔️ Выбранное время консультации больше недоступно. Пожалуйста, выберите другое время."

TEXT_APPOINTMENT_DATE_STATUS_OK = "✅"
TEXT_APPOINTMENT_DATE_STATUS_NOT_OK = "❗️"
TEXT_CONSULTATION_NOTIFICATION_STATUS_ON = "🔔"
TEXT_CONSULTATION_NOTIFICATION_STATUS_OFF = "🔕"

BUTTON_CANCEL = "❌ Отменить"
BUTTON_CLOSE = "❌ Закрыть"
BUTTON_CONFIRM = "✅ Подтвердить"
BUTTON_BACK = "◀️ Назад"
BUTTON_CONTINUE = "➡️ Продолжить"
BUTTON_ADMIN_PANEL = "🧑‍💻 Админ-панель"
BUTTON_ADMIN_PANEL_CONSULTATION_TIME = "⏰ Время приёма консультаций"
BUTTON_ADMIN_PANEL_CONSULTATION_NOTIFICATION = "Уведомления о консультациях"
BUTTON_ADMIN_PANEL_CHANGE_CONSULTATION_APPOINTMENT_TIMES = "⏰ Изменить"
BUTTON_TIMEZONE_MSC_M1 = "МСК-1"
BUTTON_TIMEZONE_MSC = "МСК"
BUTTON_TIMEZONE_MSC_P1 = "МСК+1"
BUTTON_TIMEZONE_MSC_P2 = "МСК+2"
BUTTON_TIMEZONE_MSC_P3 = "МСК+3"
BUTTON_TIMEZONE_MSC_P4 = "МСК+4"
BUTTON_TIMEZONE_MSC_P5 = "МСК+5"
BUTTON_TIMEZONE_MSC_P6 = "МСК+6"
BUTTON_TIMEZONE_MSC_P7 = "МСК+7"
BUTTON_TIMEZONE_MSC_P8 = "МСК+8"
BUTTON_TIMEZONE_MSC_P9 = "МСК+9"
BUTTON_CONSULTATION = "📞 Консультация"
BUTTON_CONSULTATION_TG_PHONE_NUMBER = "Номер Telegram"
BUTTON_CONSULTATION_ANSWER_HSK1 = "HSK 1"
BUTTON_CONSULTATION_ANSWER_HSK2 = "HSK 2"
BUTTON_CONSULTATION_ANSWER_HSK3 = "HSK 3"
BUTTON_CONSULTATION_ANSWER_HSK4 = "HSK 4"
BUTTON_CONSULTATION_ANSWER_HSK5 = "HSK 5"
BUTTON_CONSULTATION_ANSWER_HSK6 = "HSK 6"
BUTTON_CONSULTATION_ANSWER_IDK = "Не знаю"
BUTTON_CONSULTATION_ANSWER_ZERO = "Нулевой"
BUTTON_CONSULTATION_ANSWER_NO_HOW = "Никак"
BUTTON_CONSULTATION_ANSWER_ONLINE_COURCES = "Онлайн-курсы"
BUTTON_CONSULTATION_ANSWER_ONLINE_TEACHER = "Онлайн с репетитором"
BUTTON_CONSULTATION_ANSWER_OFFLINE_TEACHER = "Репетитор в жизни"
BUTTON_CONSULTATION_ANSWER_GROUP_LESSONS = "Групповые занятия"
BUTTON_CONSULTATION_ANSWER_INDEPENDENTLY = "Самостоятельно"
BUTTON_CONSULTATION_SELECT_TIME = "🗓 Выбрать время"
BUTTON_CONSULTATION_CHANGE_TIME = "🗓 Изменить время"
BUTTON_CONSULTATION_MARK_AS_PROCESSED = "✅ Выполнена"

TEXT_DESCRIPTION_MENU_COMMAND = "Открывает меню"

COMMAND_MESSAGE_START = "start"
COMMAND_MESSAGE_MENU = 'menu'

COMMAND_CALLBACK_QUERY_CONSULTATION = "consultation"
COMMAND_CALLBACK_QUERY_MENU = 'menu'
COMMAND_CALLBACK_QUERY_ADMIN_PANEL = "admin_panel"