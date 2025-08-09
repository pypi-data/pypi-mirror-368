import random
from string import digits, ascii_lowercase, ascii_uppercase

from names import get_first_name


class Account:
    def __init__(self, **kwargs):
        self.first_name = kwargs.get("first_name", get_first_name())
        self.last_name = kwargs.get("last_name", get_first_name())
        self.full_name = self.first_name + " " + self.last_name
        domain = kwargs.get("domain", 'gmail.com')
        if 'username' in kwargs.keys():
            self.username = kwargs["username"]
        elif 'email_length' in kwargs.keys():
            self.username = generate_username(self.first_name, kwargs["email_length"] - len(domain))
        elif 'username_length' in kwargs.keys():
            self.username = generate_username(self.first_name, kwargs["username_length"])
        else:
            self.username = generate_username(self.first_name)
        self.email = kwargs.get("email", f'{self.username}@{domain}')
        password_length = kwargs.get("password_length", None)
        additional_characters = kwargs.get('additional_characters', '')
        self.password = kwargs.get("password", generate_password(password_length, additional_characters))
        self.phone_number = generate_us_number()
        self.address_line1 = generate_address_line_1()
        self.city = get_random_city()


def generate_username(name: str = get_first_name(), length: int = random.randint(10, 15)):
    return f'{name}{"".join(random.choice(digits) for _ in range(length - len(name)))}'.lower()


def generate_password(length: int | None = None, additional_characters: str = ''):
    if length is None:
        length = random.randint(10, 20)
    while True:
        try:
            character_set = ascii_lowercase + ascii_uppercase + digits + additional_characters
            password = ''.join(random.choice(character_set) for _ in range(length))
            contains_lower = any(character in ascii_lowercase for character in password)
            contains_upper = any(character in ascii_uppercase for character in password)
            contains_digit = any(character.isdigit() for character in password)
            contains_others = any(character in additional_characters for character in password)
            contains_both_cases = contains_lower and contains_upper
            if contains_digit and (contains_others if additional_characters else True) and contains_both_cases:
                return password
            else:
                return generate_password(length, additional_characters)
        except RecursionError:
            pass


def generate_us_number():
    area_code = str(random.randint(200, 999))         # Avoids starting with 0 or 1
    exchange_code = str(random.randint(200, 999))     # Same here
    subscriber_number = str(random.randint(0, 9999)).zfill(4)

    return f"{area_code}{exchange_code}{subscriber_number}"


def generate_address_line_1():
    street_numbers = range(100, 9999)
    street_names = [
        "Main", "Oak", "Pine", "Maple", "Cedar", "Elm", "Washington", "Lake", "Hill", "Sunset"
    ]
    street_types = ["St", "Ave", "Blvd", "Rd", "Ln", "Dr", "Ct", "Pl", "Way", "Terrace"]

    number = str(random.choice(street_numbers))
    name = random.choice(street_names)
    st_type = random.choice(street_types)

    return f"{number} {name} {st_type}"


def get_random_city():
    cities = [
        "New York", "Tokyo", "London", "Paris", "Berlin",
        "Cairo", "Dubai", "Istanbul", "Sydney", "Toronto",
        "Rio de Janeiro", "Moscow", "Seoul", "Bangkok", "Mumbai"
    ]
    return random.choice(cities)