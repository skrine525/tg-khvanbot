import random, string, os, json

# Переменная системных путей
class SystemPaths:
    # Директории
    ROOT_DIR = os.getcwd()
    #TMP_DIR = os.path.join(ROOT_DIR, 'tmp')
    #SRC_DIR = os.path.join(ROOT_DIR, 'src')

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

# Функция инициализации системных директорий
def initdir():
    # tmp/
    if not os.path.exists(SystemPaths.TMP_DIR):
        os.mkdir(SystemPaths.TMP_DIR)
