# scheduling-api/test_mongo.py
from db import ping, users_col
from auth_helpers import is_valid_email, hash_password

print("ping:", ping())   # should return {'ok': 1.0} if Mongo is running

if is_valid_email("alice@example.com"):
    doc = {"username":"alice@example.com", "password": hash_password("secret123"), "company_name":"Acme"}
    result = users_col.insert_one(doc)
    print("Inserted user id:", result.inserted_id)
else:
    print("Email invalid")
