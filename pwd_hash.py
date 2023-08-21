import bcrypt

# Read the salt from the file
with open("salt.txt", "rb") as salt_file:
    salt = salt_file.read()

def hash(pwd):
    hashed_password = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
    return hashed_password

def check_password(pwd, hashed_password):
    is_password_correct = bcrypt.checkpw(pwd.encode("utf-8"), hashed_password)
    return is_password_correct

