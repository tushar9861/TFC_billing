"""
Test script to diagnose the exact Firestore write error for license_keys.
Run this while the dashboard is closed.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from firestore_rest import firestore as db

# Prompt for credentials
email = input("Enter your admin email: ").strip()
pwd = input("Enter your password: ").strip()

print("\n[1] Logging in...")
try:
    data = db.login(email, pwd)
    print(f"    OK. Token: {db.id_token[:40]}...")
except Exception as e:
    print(f"    FAILED: {e}")
    sys.exit(1)

print("\n[2] Testing write to license_keys (Firestore)...")
import random, string, datetime
test_key = "TEST-" + ''.join(random.choices(string.ascii_uppercase, k=8))
try:
    result = db.set_document(f"license_keys/{test_key}", {
        "license_key": test_key,
        "email_intended": "test@test.com",
        "package_type": "Test",
        "distributor_id": "direct",
        "is_used": False,
        "created_at": datetime.datetime.now().isoformat()
    })
    print(f"    SUCCESS! Key {test_key} written to Firestore.")
except Exception as e:
    print(f"    FAILED with: {type(e).__name__}: {e}")
    # If it's an HTTPError, show the response body
    if hasattr(e, 'response'):
        print(f"    HTTP Status: {e.response.status_code}")
        print(f"    Response body: {e.response.text}")

print("\n[3] Testing unauthenticated write (no token)...")
saved_token = db.id_token
db.id_token = None
try:
    db.set_document(f"license_keys/UNAUTH-TEST", {
        "test": True
    })
    print("    Succeeded without auth (rules are open)")
except Exception as e:
    print(f"    Failed without auth (expected): {type(e).__name__}")
    if hasattr(e, 'response'):
        print(f"    Status: {e.response.status_code}")
db.id_token = saved_token
