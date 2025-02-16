import random
from book_operations import export_books_to_csv, list_books
from connection import connect, config
from validation import validate_password, validate_phone, validate_email, validate_date_of_birth, validate_isbn, validate_year


def register_user():
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    username = input("Enter username: ")
    password = input("Enter password: ")
    email = input("Enter email: ")

    # Validate email and password
    if not validate_email(email):
        print("Invalid email format!")
        return

    if not validate_password(password):
        print("Password must contain at least one uppercase, one lowercase, one digit, and one special character.")
        return


    birth_date = input("Enter date of birth (YYYY-MM-DD): ")
    phone_number = input("Enter phone number: ")

    # Validate phone number and date of birth
    if not validate_phone(phone_number):
        print("Invalid phone number. It should contain 10 digits.")
        return

    if not validate_date_of_birth(birth_date):
        print("Invalid birth date format. Use YYYY-MM-DD.")
        return

    # Randomly assign role (admin or guest)
    role = random.choice(["admin", "guest"])


    role_query = "SELECT id FROM roles WHERE role_name = %s"
    conn, cursor = connect(config, role_query, role)

    # Insert user into the database
    if cursor:
        role_id = cursor.fetchone()[0]
        insert_user_sql = """
        INSERT INTO users (username, password, email, first_name, last_name, birth_date, phone_number, role_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        conn, cursor = connect(config, insert_user_sql, username, password, email, first_name, last_name, birth_date, phone_number, role_id)
        if cursor:
            conn.commit()
            print(f"User registered successfully with role {role.capitalize()}!")
        else:
            print("Failed to register user.")
        conn.close()
    else:
        print("Failed to fetch role ID.")
        conn.close()


# User Login
def login_user():
    username = input("Enter username: ")
    password = input("Enter password: ")

    query = "SELECT * FROM users WHERE username = %s AND password = %s"

    conn, cursor = connect(config, query, username, password)

    if cursor:
        user = cursor.fetchone()
        if user:
            print(f"Login successful! Welcome {user[4]}.")
            role_id = user[8]

            role_query = "SELECT role_name FROM roles WHERE id = %s"
            conn, cursor = connect(config, role_query, role_id)

            if cursor:
                role_data = cursor.fetchone()
                if role_data:
                    role = role_data[0]
                else:
                    role = "unknown"

            conn.close()
            return user, role
        else:
            print("Invalid username or password!")
            conn.close()
            return None, None
    else:
        print("Database error.")
        return None, None


def admin_operations():
    while True:
        print("\nAdmin Operations:")
        print("1. Add Book")
        print("2. Delete Book")
        print("3. Modify Book")
        print("4. List Books")
        print("5. Log out")
        choice = input("Choose an option: ")

        if choice == "1":
            title = input("Enter title: ")
            authors = input("Enter authors: ")
            isbn = input("Enter ISBN: ")

            # ISBN validation
            if not validate_isbn(isbn):
                print("Invalid ISBN format! ISBN should be exactly 5 digits.")
                continue

            # publication year validation
            year = input("Enter publication year (4 digits): ")
            if not validate_year(year):
                print("Invalid year! Please enter a 4-digit year.")
                continue
            year = int(year)

            query = "INSERT INTO books (title, authors, isbn, year) VALUES (%s, %s, %s, %s)"
            conn, cursor = connect(config, query, title, authors, isbn, year)
            conn.commit()
            print("Book added successfully!")
            conn.close()

        elif choice == "2":
            isbn = input("Enter ISBN of the book to delete: ")

            # ISBN validation
            if not validate_isbn(isbn):
                print("Invalid ISBN format! ISBN should be exactly 5 digits.")
                continue

            # Check if book exists according to the given ISBN
            query = "SELECT * FROM books WHERE isbn = %s"
            conn, cursor = connect(config, query, isbn)
            book = cursor.fetchone()

            if not book:
                print("No book found with the given ISBN. Deletion failed.")
                continue

            # delete a book
            delete_query = "DELETE FROM books WHERE isbn = %s"
            conn, cursor = connect(config, delete_query, isbn)
            conn.commit()


            query = "SELECT * FROM books WHERE isbn = %s"
            conn, cursor = connect(config, query, isbn)
            book = cursor.fetchone()

            if book:
                print("Failed to delete the book. It might still exist.")
            else:
                print("Book deleted successfully!")

            conn.close()

        elif choice == "3":
            isbn = input("Enter ISBN of the book to modify: ")

            # ISBN validation
            if not validate_isbn(isbn):
                print("Invalid ISBN format! ISBN should be exactly 5 digits.")
                continue

            query = "SELECT * FROM books WHERE isbn = %s"
            conn, cursor = connect(config, query, isbn)

            if cursor:
                book = cursor.fetchone()
                if not book:
                    print("Book not found!")
                    continue

                print(f"Current details: Title: {book[1]}, Authors: {book[2]}, ISBN: {book[3]}, Year: {book[4]}")

                new_title = input(f"Enter new title if it needs to be changed (current: {book[1]}): ")
                new_authors = input(f"Enter new authors if it needs to be changed (current: {book[2]}): ")
                new_year = input(f"Enter new publication year if it needs to be changed (current: {book[4]}): ")

                # publication year validation
                if new_year and not validate_year(new_year):
                    print("Invalid year! Please enter a 4-digit year.")
                    continue
                new_year = int(new_year) if new_year else book[4]
                new_title = new_title if new_title else book[1]
                new_authors = new_authors if new_authors else book[2]

                update_query = """
                UPDATE books 
                SET title = %s, authors = %s, year = %s 
                WHERE isbn = %s
                """
                conn, cursor = connect(config, update_query, new_title, new_authors, new_year, isbn)
                if cursor:
                    conn.commit()
                    print("Book updated successfully!")
                    conn.close()
                else:
                    print("Failed to update book.")
                    conn.close()

        elif choice == "4":
            filter_by = input("Filter by (title/authors/isbn/year): ").lower()

            if filter_by == "isbn":
                isbn = input("Enter ISBN to filter by: ").strip()

                # ISBN validation
                if not validate_isbn(isbn):
                    print("Invalid ISBN format! ISBN should be exactly 5 digits.")
                    continue

                books = list_books(filter_by, isbn)
                if not books:
                    print("No book found with the given ISBN.")

            elif filter_by == "year":
                filter_value_1 = input("Enter start year (4 digits): ")
                filter_value_2 = input("Enter end year (4 digits): ")

                # publication year validation
                if not validate_year(filter_value_1) or not validate_year(filter_value_2):
                    print("Invalid year! Please enter 4-digit years.")
                    continue

                books = list_books(filter_by, filter_value_1, filter_value_2)
            else:
                filter_value = input("Enter filter value: ").strip()
                books = list_books(filter_by, filter_value)

            if books:
                print(f"\nList of books filtered by {filter_by}:")
                for book in books:
                    print(f"Title: {book[1]}, Authors: {book[2]}, ISBN: {book[3]}, Year: {book[4]}")

                export_choice = input("Do you want to export the list to a CSV file? (y/n): ").strip().lower()
                if export_choice == "y":
                    export_books_to_csv(books)

        elif choice == "5":
            print("Logging out...")
            break


def guest_operations():
    while True:
        print("\nGuest Operations:")
        print("1. List Books")
        print("2. Log out")
        choice = input("Choose an option: ")

        if choice == "1":
            filter_by = input("Filter by (title/authors/isbn/year): ").lower()

            if filter_by == "isbn":
                isbn = input("Enter ISBN to filter by: ").strip()

                # ISBN validation
                if not validate_isbn(isbn):
                    print("Invalid ISBN format! ISBN should be exactly 5 digits.")
                    continue

                books = list_books(filter_by, isbn)
                if not books:
                    continue
            #publication year validation
            elif filter_by == "year":
                filter_value_1 = input("Enter start year: ")
                filter_value_2 = input("Enter end year: ")


                try:
                    int(filter_value_1)
                    int(filter_value_2)
                except ValueError:
                    print("Invalid year input. Please provide numeric values for both start and end years.")
                    continue

                books = list_books(filter_by, filter_value_1, filter_value_2)
            else:
                filter_value = input("Enter filter value: ").strip()
                books = list_books(filter_by, filter_value)

            if books:
                print(f"\nList of books filtered by {filter_by}:")
                for book in books:
                    print(f"Title: {book[1]}, Authors: {book[2]}, ISBN: {book[3]}, Year: {book[4]}")

                export_choice = input("Do you want to export the list to a CSV file? (y/n): ").strip().lower()
                if export_choice == "y":
                    export_books_to_csv(books)

        elif choice == "2":
            print("Logging out...")
            break