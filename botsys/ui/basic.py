import telebot
from botsys.core import strcontent
from botsys.core.bot import Bot
from botsys.db.model import Database, User
from botsys.db.behavior import check_user


def start_message_command(bot: Bot, message: telebot.types.Message):
    # База данных
    session = Database.make_session()
    db_user = session.query(User).filter_by(tg_user_id=message.from_user.id).first()
    db_user = check_user(session, db_user, message.from_user.id)
    session.close()

    bot.send_message(message.chat.id, strcontent.MESSAGE_HELLO)
    