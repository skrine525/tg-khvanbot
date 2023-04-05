# Модуль, содержащий все строковые константы, используемые в боте


MESSAGE_COMMANDS_NOT_AVAILABLE_TO_ANONYMOUS_IN_GROUP = "⛔️ Команды недоступны для анонимных в группе пользователей."
MESSAGE_INVALID_INLINE_KEYBOARD_TOKEN = "⛔️ Эта функция недоступна. Вызовите новое меню."
MESSAGE_UNKNOWN_USER = "К сожалению, мы вас не знаем. Нажмите на /start и пройдите регистраци."
MESSAGE_ALREADY_REGISTERED = "Вы уже зарегистрированы и вам доступны все функции."
MESSAGE_NEED_REGISTRATION = "⛔️ Для начала необходимо зарегистрироваться.\nНажмите на /start для прохождения регистрации."
MESSAGE_START = "Привет и добро пожаловать в школу китайского языка Венеры Хван\\. _Еще какой нибудь текст додумаем_\nА сейчас давай познакомимся\\.\n\n📝 Укажи свое *имя*\\."
MESSAGE_REGISTRATION_TOO_LONG_FIRST_NAME = "Введеное имя слишком длинное.\nУкажите, например, короткую форму имени."
MESSAGE_REGISTRATION_STAGE_1 = "Привет, {first_name}\\. Приятно с тобой познакомиться\\.\n\n📝Теперь укажи свою *фамилию*\\."
MESSAGE_REGISTRATION_STAGE_2 = "1️⃣ *Имя*: {first_name}\n2️⃣ *Фамилия*: {last_name}\n\nОсталось только *отчество*\\. Напиши его\\."
MESSAGE_REGISTRATION_STAGE_3 = "2️⃣ *Имя*: {first_name}\n2️⃣ *Фамилия*: {last_name}\n3️⃣ *Отчество*: {middle_name}\n\n🔘 Выбери свой *часовой пояс*\\."
MESSAGE_REGISTRATION_STAGE_4 = "2️⃣ *Имя*: {first_name}\n2️⃣ *Фамилия*: {last_name}\n3️⃣ *Отчество*: {middle_name}\n4️⃣ *Часовой пояс*: {timezone}\n\n✅ Регистрация пройдена\\."
MESSAGE_OFFER_CONSULTATION = "📞 Теперь ты можешь записаться на консультацию."
MESSAGE_CONSULTATION_STAGE_1 = "Отлично! Давай запишем тебя на консультацию.\n\nДля начала необходимо указать номер телефона. Ты можешь предоставить номер Telegram или указать другой."
MESSAGE_CONSULTATION_STAGE_2 = "Номер получен. Теперь необходимо ответить на несколько вопросов.\n\nКакой у вас уровень китайского языка?\n• HSK 1 (примерно 150 иероглифов)\n• HSK 2 (примерно 300 иероглифов)\n• HSK 3 (примерно 600 иероглифов)\n• HSK 4 (примерно 1200 иероглифов)\n• HSK 5 (примерно 2500 иероглифов)\n• HSK 6 😎\n• Нулевой (еще не начинал(а) изучать)\n• Не знаю"
MESSAGE_CONSULTATION_STAGE_3 = "Планируете сдавать экзамен HSK? (Если да, то когда и какой уровень хотели бы сдать?).\n\nНапиши письменный ответ."
MESSAGE_CONSULTATION_STAGE_4 = "Какая цель на китайский язык сейчас?\n\nНапиши письменный ответ."
MESSAGE_CONSULTATION_STAGE_5 = "Как Вы сейчас изучаете язык?\n• Никак\n• Онлайн-курсы\n• Онлайн с репетитором\n• Встречаюсь с репетитором (очно)\n• Хожу на групповые занятия\n• Самостоятельно (смотрю ютуб, дорамы, решаю тесты и др.)"
MESSAGE_CONSULTATION_STAGE_6 = "✅ Анкета заполнена. Теперь выбери удобное время консультации."
MESSAGE_CONSULTATION_HELP_1 = "Предоставь номер телефона Telegram или укажи другой номер телефона."
MESSAGE_CONSULTATION_CANCELED = "✅ Создание заявки на консультацию отменено."
MESSAGE_CONSULTATION_TELL_PHONE_NUMBER = "Укажите номер телефона без кода +7."
MESSAGE_CONSULTATION_CREATION_ERROR = "⛔️ Произошла ошибка. Попробуйте еще раз записаться на консультацию."
MESSAGE_CONSULTATION_TOO_LONG_ANSWER = "⛔️ Ответ содержит более 100 символов. Пожалуйста, напишите ответ короче."
MESSAGE_CONSULTATION_SELECT_TIME_1 = "🗓 Выберите удобное время консультации."
MESSAGE_CONSULTATION_SELECT_TIME_2 = "🗓 Выберите дату."
MESSAGE_CONSULTATION_SELECT_TIME_3 = "📅 *Дата*: {date}\n\n🗓 Выберите время\\."
MESSAGE_CONSULTATION_CONFIRMATION = "👤 *Имя*: {user_name}\n☎️ *Телефон*: {phone_number}\n📅 *Дата*: {date}\n⏰ *Время*: {time}\n\n📝 *Ответы на вопросы*:\n\n*В*: Какой у вас уровень китайского языка?\n*О*: {lang_level}\n\n*В*: Планируете сдавать экзамен HSK? \\(Если да, то когда и какой уровень хотели бы сдать?\\)\n*О*: {hsk_exam}\n\n*В*: Какая цель на китайский язык сейчас?\n*О*: {purpose}\n\n*В*: Как Вы сейчас изучаете язык?\n*О*: {way_now}"
MESSAGE_CONSULTATION_SENT = "✅ Консультация №{consultation_id} запрошена. С вами свяжуться в указанное время."

NOTIFICATION_UNKNOWN_COMMAND = "⛔️ Неизвестная команда."
NOTIFICATION_YOU_DO_NOT_HAVE_ACCESS_TO_THIS_MENU = "⛔️ У вас нет доступа к этому меню."
NOTIFICATION_NEED_REGISTRATION = "⛔️ Для начала необходимо зарегистрироваться."
NOTIFICATION_YOU_HAVE_ALREADY_ACTIVE_CONSULTATION = "⛔️ Вы уже создали запрос на консультацию. С вами должны связаться в указанное время."

BUTTON_CANCEL = "❌ Отменить"
BUTTON_CONFIRM = "✅ Подтвердить"
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
BUTTON_CONSULTATION = "Получить консультацию"
BUTTON_CONSULTATION_TG_PHONE_NUMBER = "Номер Telegram"
BUTTON_CONSULTATION_TELL_PHONE_NUMBER = "Указать номер"
BUTTON_CONSULTATION_ANSWER_HSK1 = "HSK 1"
BUTTON_CONSULTATION_ANSWER_HSK2 = "HSK 2"
BUTTON_CONSULTATION_ANSWER_HSK3 = "HSK 3"
BUTTON_CONSULTATION_ANSWER_HSK4 = "HSK 4"
BUTTON_CONSULTATION_ANSWER_HSK5 = "HSK 5"
BUTTON_CONSULTATION_ANSWER_HSK6 = "HSK 6"
BUTTON_CONSULTATION_ANSWER_IDK = "Не знаю"
BUTTON_CONSULTATION_ANSWER_ZERO = "Нулевой"
BUTTON_CONSULTATION_ANSWER_NO_HOW = "Никак"
BUTTON_CONSULTATION_ANSWER_ONLINE_СOURSES = "Онлайн-курсы"
BUTTON_CONSULTATION_ANSWER_ONLINE_TEACHER = "Онлайн с репетитором"
BUTTON_CONSULTATION_ANSWER_OFFLINE_TEACHER = "Репетитор в жизни"
BUTTON_CONSULTATION_ANSWER_GROUP_LESSONS = "Групповые занятия"
BUTTON_CONSULTATION_ANSWER_INDEPENDENTLY = "Самостоятельно"
BUTTON_CONSULTATION_SELECT_TIME = "🗓 Выбрать время"
BUTTON_CONSULTATION_CHANGE_TIME = "🗓 Изменить время"

TEXT_DESCRIPTION_MENU_COMMAND = "Открывает меню"

COMMAND_MESSAGE_START = "start"
COMMAND_MESSAGE_MENU = 'menu'

COMMAND_CALLBACK_QUERY_CONSULTATION = "consultation"
COMMAND_CALLBACK_QUERY_MENU = 'menu'