from firestore_rest import firestore as db
import requests
import sys

email = "odibrix@gmail.com"
pwd = "testpassword123"

try:
    print("Trying signup...")
    db.signup(email, pwd)
    print("Signup succeeded")
except requests.exceptions.HTTPError as e:
    print(f"Signup HTTPError: {e.response.status_code}")
    print(f"Signup Error Body: {e.response.text}")
    if "EMAIL_EXISTS" in e.response.text:
        try:
            print("Trying login instead...")
            # We don't know the password they actually used, so this will fail with INVALID_PASSWORD
            db.login(email, "somepassword")
        except requests.exceptions.HTTPError as e2:
            print(f"Login HTTPError: {e2.response.status_code}")
            print(f"Login Error Body: {e2.response.text}")

