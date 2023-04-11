import random, string, os, json

# Переменная системных путей
class SystemPaths:
    # Директории
    ROOT_DIR = os.getcwd()
    LOG_DIR = os.path.join(ROOT_DIR, 'log')
    LOG_FILE = os.path.join(LOG_DIR, 'bot.log')

# Генерация случайной строки
def generate_random_string(length, uppercase=True, lowercase=True, numbers=True):
    letters = ''
    if uppercase and lowercase:
        letters = string.ascii_letters
    elif uppercase:
        letters = string.ascii_uppercase
    elif lowercase:
        letters = string.ascii_lowercase
    if numbers:
        letters += '0123456789'

    return ''.join(random.choice(letters) for _ in range(length))

# Генерация списка рядов для клавиатур
def get_keyboard_row_list(buttons: list, row_width: int = 3):
    rows = []
    curr_index = 0
    curr_row_button_count = 0
    for i in buttons:
        curr_row_button_count += 1
        if curr_row_button_count > row_width:
            curr_row_button_count = 1
            curr_index += 1
        try:
            rows[curr_index].append(i)
        except IndexError:
            rows.append([i])
    return rows

# Экранирует символы MarkdownV2
def escape_markdownv2_text(text:str):
    characters = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    escaped_text = ""
    for i in list(text):
        if i in characters:
            escaped_text += f"\\{i}"
        else:
            escaped_text += i
    return escaped_text

# Функция инициализации системных директорий
def initdirs():
    # log/
    if not os.path.exists(SystemPaths.LOG_DIR):
        os.mkdir(SystemPaths.LOG_DIR)
