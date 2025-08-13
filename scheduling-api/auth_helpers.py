# scheduling-api/auth_helpers.py
from email_validator import validate_email, EmailNotValidError
import bcrypt
from datetime import datetime
from db import users_col

def is_valid_email(email):
    try:
        validate_email(email)   # throws EmailNotValidError if invalid
        return True
    except EmailNotValidError:
        return False
    
def normalize_email(email: str) -> str:
    return (email or "").strip().lower()    

def hash_password(raw_password):
    return bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(raw_password, hashed):
    return bcrypt.checkpw(raw_password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(username_email, password, company_name, role):
    u = normalize_email(username_email)
    if not is_valid_email(u):
        raise ValueError("username must be a valid email address")

    if users_col.find_one({"username": u}):
        raise ValueError("Username already exists")

    hashed = hash_password(password)
    user_doc = {
        "username": u,
        "password": hashed,
        "company_name": company_name,
        "role": role,
        "created_at": datetime.utcnow()
    }
    users_col.insert_one(user_doc)
    # do not return password
    user_doc.pop("password")
    return user_doc