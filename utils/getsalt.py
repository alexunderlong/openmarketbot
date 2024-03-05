import random

def getsalt():
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-={}[]\"\',./?~`№;%"
    chars = []
    for i in range(16):
        chars.append(random.choice(alphabet))
    salt = "".join(chars)
    return salt
