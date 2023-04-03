import botsys.core.strcontent as strcontent
from botsys.ui.basic import ConsultationCommand, MenuCommand, start_message_command
from botsys.core.bot import Bot


def register_commands(bot: Bot):
    bot.register_message_command(strcontent.COMMAND_MESSAGE_START, start_message_command)
    bot.register_message_command(strcontent.COMMAND_MESSAGE_MENU, MenuCommand.message_command, description=strcontent.TEXT_DESCRIPTION_MENU_COMMAND, add_to_menu=True)

    bot.register_callback_query_command(strcontent.COMMAND_CALLBACK_QUERY_CONSULTATION, ConsultationCommand.callback_query_command)

    # Устанавливаем команды в меню бота
    bot.set_commands_menu()