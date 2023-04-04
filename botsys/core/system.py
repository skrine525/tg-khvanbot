import random, string, os, json

# Переменная системных путей
class SystemPaths:
    # Директории
    ROOT_DIR = os.getcwd()

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

# Функция инициализации системных директорий
def initdir():
    # tmp/
    if not os.path.exists(SystemPaths.TMP_DIR):
        os.mkdir(SystemPaths.TMP_DIR)
