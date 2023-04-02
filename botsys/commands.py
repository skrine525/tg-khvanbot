import botsys.core.strcontent as strcontent
from botsys.ui.basic import start_message_command
from botsys.core.bot import Bot


def register_commands(bot: Bot):
    bot.register_message_command(strcontent.COMMAND_MESSAGE_START, start_message_command, '')

    # Устанавливаем команды в меню бота
    bot.set_commands_menu()