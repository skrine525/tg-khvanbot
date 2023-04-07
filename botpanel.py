import config
from botsys.db.behavior import Database
from botsys.db.model import User, UserRole, Admin

Database.create_engine(config.SQLALCHEMY_URL)

print("Write 'command-list' to get command list.")
while True:
    command = input(">> ")

    if command == "command-list":
        commands = ['command-list', 'exit', 'delete-user', 'delete-role', 'set-role-admin']
        print('\n'.join(commands))
    elif command == "exit":
        break
    elif command == "delete-user":
        user_id = int(input("User ID: "))
        session = Database.make_session()
        user = session.query(User).filter_by(user_id=user_id).first()
        if user is None:
            print("User not found.")
        else:
            user_fullname = user.get_full_name()
            print(f"User: {user_fullname}")
            answers = ['y', 'n', 'yes', 'no']
            answer = ""
            while not (answer in answers):
                answer = input("Delete User? ")
            if answer in ['y', 'yes']:
                session.delete(user)
                session.commit()
                print("User deleted.")
            session.close()
    elif command == 'set-role-admin':
        user_id = int(input("User ID: "))
        session = Database.make_session()
        user = session.query(User).filter_by(user_id=user_id).first()

        if user is None:
            print("User not found.")
        elif user.role is not None:
            print("User has role already.")
        else:
            user_fullname = user.get_full_name()
            print(f"User: {user_fullname}")
            answers = ['y', 'n', 'yes', 'no']
            answer = ""
            while not (answer in answers):
                answer = input("Set Admin role to User? ")
            if answer in ['y', 'yes']:
                role = UserRole(user.user_id, UserRole.ROLE_ADMIN)
                session.add(role)
                session.commit()
                admin = Admin(role.user_role_id)
                session.add(admin)
                session.commit()
                print("Done.")
            session.close()
    elif command == "delete-role":
        user_id = int(input("User ID: "))
        session = Database.make_session()
        user = session.query(User).filter_by(user_id=user_id).first()
        if user is None:
            print("User not found.")
        elif user.role is None:
            print("User has no role.")
        else:
            user_fullname = user.get_full_name()
            print(f"User: {user_fullname}\nRole: {user.role.role}")
            
            answers = ['y', 'n', 'yes', 'no']
            answer = ""
            while not (answer in answers):
                answer = input("Delete User role? ")
            if answer in ['y', 'yes']:
                session.delete(user.role)
                session.commit()
                print("User role deleted.")
            session.close()
    else:
        print("Unknown command. Write 'command-list' to get command list.")
    print("\n", end="")
