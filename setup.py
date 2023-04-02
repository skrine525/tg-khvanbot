import os
import botsys.db.model as model
from sqlalchemy import create_engine

# Строки config.py
CONFIG_FILE_LINES = ['BOT_TOKEN = ""', 'SQLALCHEMY_URL = ""']

if __name__ == "__main__":
    # Создание файла config.py
    if not os.path.exists("config.py"):
        print("Creating config.py...")
        config_file = open("config.py", "w")
        config_file.write('\n'.join(CONFIG_FILE_LINES))
        config_file.close()

    # Создание таблиц базы данных
    import config as config
    if config.SQLALCHEMY_URL != '':
        print("Creating database...")
        engine = create_engine(config.SQLALCHEMY_URL, echo=True)
        model.Database.Base.metadata.create_all(engine)
    else:
        print("Please, adjust config.py")

