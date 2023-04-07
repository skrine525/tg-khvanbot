import config
from botsys.db.behavior import Database
from botsys.db.model import User

Database.create_engine(config.SQLALCHEMY_URL)

print("Write 'command-list' to get command list.")
while True:
    command = input(">> ")

    if command == "command-list":
        commands = ['command-list', 'exit', 'delete-user']
        print('\n'.join(commands))
    elif command == "exit":
        break
    elif command == "delete-user":
        user_id = int(input("User ID: "))
        session = Database.make_session()
        db_user = session.query(User).filter_by(user_id=user_id).first()
        if db_user is None:
            print("User not found.")
        else:
            user_fullname = db_user.get_full_name()
            print(f"Fullname: {user_fullname}")
            answers = ['y', 'n', 'yes', 'no']
            answer = ""
            while not (answer in answers):
                answer = input("Delet User? ")
            if answer in ['y', 'yes']:
                session.delete(db_user)
                session.commit()
                print("User deleted.")
            session.close()
    else:
        print("Unknown command.")
    print("\n", end="")
