import random
import string




def generate_random_otp():
    return random.randint(100000, 999999)


def generate_random_voting_number():

     return ''.join(random.choice(string.ascii_letters) for _ in range(6))


