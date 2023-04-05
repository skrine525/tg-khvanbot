from botsys.core.system import initdir
from botsys.core.bot import Bot
from botsys.commands import register_commands
from botsys.db.model import Database
from config import BOT_TOKEN, SQLALCHEMY_URL


# Инициализация разных компонентов
#initdir()
Database.create_engine(SQLALCHEMY_URL)

# Инициализация бота
bot = Bot(BOT_TOKEN)

# Регистрация команд
register_commands(bot)

if __name__ == "__main__":
    # Запуск прослушивание
    bot.infinity_polling()