import psycopg2

config = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost'
}


def connect(config, query, *args):
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        if args:
            cursor.execute(query, args)
        else:
            cursor.execute(query)
        return conn, cursor
    except psycopg2.DatabaseError as error:
        print(f"Database error: {error}")
        return None, None


# Create tables and insert data
def create_tables_and_insert_data():
    create_roles_table_sql = """
    CREATE TABLE IF NOT EXISTS roles (
        id SERIAL PRIMARY KEY,
        role_name VARCHAR(50) UNIQUE NOT NULL
    );
    """

    insert_roles_sql = """
    INSERT INTO roles (role_name) VALUES
    ('admin'),
    ('guest')
    ON CONFLICT (role_name) DO NOTHING;
    """

    create_users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        birth_date DATE,
        phone_number VARCHAR(15),
        role_id INTEGER REFERENCES roles(id)
    );
    """

    create_books_table_sql = """
    CREATE TABLE IF NOT EXISTS books (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        authors VARCHAR(255) NOT NULL,
        isbn VARCHAR(50) NOT NULL UNIQUE,
        year INTEGER NOT NULL
    );
    """

    insert_books_sql = """
    INSERT INTO books (title, authors, isbn, year) VALUES
    ('Harry Potter and the Philosophers Stone', 'J.K. Rowling', '12345', 1997),
    ('Harry Potter and the Chamber of Secrets', 'J.K. Rowling', '67890', 1998),
    ('Harry Potter and the Prisoner of Azkaban', 'J.K. Rowling', '11123', 1999),
    ('1984', 'George Orwell', '34356', 1949),
    ('Animal Farm', 'George Orwell', '61626', 1945),
    ('The Hobbit', 'J.R.R. Tolkien', '62636', 1937),
    ('The Lord of the Rings', 'J.R.R. Tolkien', '64656', 1954),
    ('Pride and Prejudice', 'Jane Austen', '66676', 1813),
    ('Sense and Sensibility', 'Jane Austen', '68697', 1811),
    ('The Great Gatsby', 'F. Scott Fitzgerald', '71727', 1925),
    ('To Kill a Mockingbird', 'Harper Lee', '73747', 1960),
    ('The Adventures of Huckleberry Finn', 'Mark Twain', '75567', 1884),
    ('The Adventures of Tom Sawyer', 'Mark Twain', '77778', 1876),
    ('The Old Man and the Sea', 'Ernest Hemingway', '81828', 1952),
    ('War and Peace', 'Leo Tolstoy', '83848', 1869),
    ('Anna Karenina', 'Leo Tolstoy', '85868', 1877),
    ('A Tale of Two Cities', 'Charles Dickens', '87889', 1859),
    ('Great Expectations', 'Charles Dickens', '91929', 1861),
    ('David Copperfield', 'Charles Dickens', '93949', 1850),
    ('Bleak House', 'Charles Dickens', '95969', 1853)
    ON CONFLICT (isbn) DO NOTHING;
    """

    conn, cursor = connect(config, create_roles_table_sql)

    if cursor:
        try:
            # Create the roles table if it doesn't already exist
            cursor.execute(create_roles_table_sql)

            # Check if the books and users tables exist before creating them
            cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'books'
            );
            """)
            books_table_exists = cursor.fetchone()[0]

            cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            );
            """)
            users_table_exists = cursor.fetchone()[0]

            # Only create the books and users tables if they don't exist
            if not books_table_exists:
                cursor.execute(create_books_table_sql)

            if not users_table_exists:
                cursor.execute(create_users_table_sql)

            # Insert roles and books if they do not already exist
            cursor.execute(insert_roles_sql)
            cursor.execute(insert_books_sql)

            # Commit changes to the database
            conn.commit()

            # Print success messages only if tables were created
            if not books_table_exists or not users_table_exists:
                print("Tables created and data inserted successfully.")
        except Exception as e:
            print(f"Error occurred: {e}")
            # Rollback changes if error occurs
            if conn:
                conn.rollback()
        finally:
            # Close the cursor and connection
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    else:
        print("Failed to connect or execute SQL queries.")
