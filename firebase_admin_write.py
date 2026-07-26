"""
firebase_admin_write.py
Uses the Firebase Admin SDK (serviceAccountKey.json) to write license keys.
This bypasses Firestore security rules, exactly like the old generate_license.py did.
"""
import os
import datetime

_admin_db = None
_initialized = False

def _init():
    global _admin_db, _initialized
    if _initialized:
        return _admin_db is not None
    _initialized = True
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serviceAccountKey.json")
    if not os.path.exists(key_path):
        return False
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore as admin_fs
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
        _admin_db = admin_fs.client()
        return True
    except Exception as e:
        print(f"[firebase_admin_write] Admin SDK init failed: {e}")
        return False

def write_license_key(license_key, data):
    """
    Write license key using Admin SDK (no auth rules restriction).
    Returns True on success, raises Exception on failure.
    """
    if _init() and _admin_db:
        _admin_db.collection("license_keys").document(license_key).set(data)
        return True
    raise RuntimeError("Firebase Admin SDK not available (serviceAccountKey.json missing or firebase-admin not installed).")

def write_pricing_config(data):
    if _init() and _admin_db:
        _admin_db.collection("app_config").document("pricing_settings").set(data)
        return True
    raise RuntimeError("Firebase Admin SDK not available.")

def write_theme_promo_config(data):
    if _init() and _admin_db:
        _admin_db.collection("app_config").document("theme_promo").set(data)
        return True
    raise RuntimeError("Firebase Admin SDK not available.")

def write_updater_config(version, url):
    if _init() and _admin_db:
        _admin_db.collection("app_config").document("updater").set({
            "latest_version": version,
            "download_url": url
        }, merge=True)
        return True
    raise RuntimeError("Firebase Admin SDK not available (serviceAccountKey.json missing or firebase-admin not installed).")
