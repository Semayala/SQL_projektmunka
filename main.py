from connection import create_tables_and_insert_data
from user_operations import admin_operations, guest_operations, register_user, login_user


def main():
    create_tables_and_insert_data()

    while True:
        print("\nWelcome to the Library")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            register_user()
        elif choice == "2":
            user, role = login_user()
            if user:
                if role == "admin":
                    admin_operations()
                elif role == "guest":
                    guest_operations()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == '__main__':
    main()