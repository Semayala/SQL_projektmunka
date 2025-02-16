from connection import connect, config
from validation import validate_isbn, validate_year
import re
import csv



def list_books(filter_by, filter_value_1, filter_value_2=None):
    filter_value_1 = re.sub(r'\s+', ' ', filter_value_1).strip()
    if filter_value_2:
        filter_value_2 = re.sub(r'\s+', ' ', filter_value_2).strip()

    # ISBN validation
    if filter_by == "isbn":
        if not validate_isbn(filter_value_1):
            print("Invalid ISBN format! ISBN should be exactly 5 digits.")
            return []

    # If filtering by year, we expect two values (start year and end year)
    if filter_by == "year":
        try:
            lower_year = int(filter_value_1)
            upper_year = int(filter_value_2) if filter_value_2 else lower_year
        except ValueError:
            print("Invalid year format. Please enter numeric values.")
            return []

        query = f"SELECT * FROM books WHERE year BETWEEN %s AND %s order by year ASC"
        conn, cursor = connect(config, query, lower_year, upper_year)  # Execute range filter
    else:
        query = f"SELECT * FROM books WHERE {filter_by} ILIKE %s"
        conn, cursor = connect(config, query, f"%{filter_value_1}%")

    if cursor:
        books = cursor.fetchall()
        conn.close()

        if not books:
            print(f"No books found with the given {filter_by}: {filter_value_1}")
            return []

        return books
    else:
        print("Failed to fetch books.")
        return []


# Export books to CSV
def export_books_to_csv(books):
    if books:
        with open('books_list.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Title", "Authors", "ISBN", "Year"])
            writer.writerows(books)
        print("Books will be exported to 'books_list.csv' after restarting the program!")
    else:
        print("No books to export.")