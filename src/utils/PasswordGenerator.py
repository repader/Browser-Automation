import random
import string



def generate_password(length=20, use_digits=True):
    characters = string.ascii_letters

    if use_digits:
        characters += string.digits

    password = ''.join(random.choice(characters) for _ in range(length))
    return password

