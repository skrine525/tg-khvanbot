from botsys.core.system import initdirs
from botsys.core.bot import Bot
from botsys.commands import register_commands
from botsys.db.behavior import Database
from config import BOT_TOKEN, SQLALCHEMY_URL


# Инициализация разных компонентов
initdirs()                                              # Инициализация системных директорий
Database.create_engine(SQLALCHEMY_URL)                  # Инициализация движка SQLAlchemy

# Инициализация бота
bot = Bot(BOT_TOKEN)

# Регистрация команд
register_commands(bot)

if __name__ == "__main__":
    # Запуск прослушивание
    bot.infinity_polling()