import re
from datetime import datetime


# Data Validation Functions
def validate_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zAZ0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email)

def validate_password(password):
    regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(regex, password)

def validate_phone(phone_number):
    return len(phone_number) == 10 and phone_number.isdigit()

def validate_date_of_birth(birth_date):
    try:
        datetime.strptime(birth_date, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_isbn(isbn):
    if len(isbn) == 5 and isbn.isdigit():
        return True
    return False

def validate_year(year):
    if len(year) == 4 and year.isdigit():
        return True
    return False