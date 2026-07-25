import os

def replace_in_file(file_path, replacements):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {file_path}")

replacements = [
    ('"TFC_POS"', '"SmartPOS"'),
    ("'TFC_POS'", "'SmartPOS'"),
    ('"tfc_outlet.db"', '"smartpos.db"'),
    ("'tfc_outlet.db'", "'smartpos.db'"),
    ('"TFC (TIWARI\'S FRIED CHICKEN) 🐔"', '"SmartPOS Restaurant"'),
    ('f"TFC{random.randint(10000, 99999)}"', 'f"INV{random.randint(10000, 99999)}"'),
    ('"TFC POS - Login"', '"SmartPOS - Login"'),
    ('"🐔 TFC POS"', '"SmartPOS"'),
    ('see you soon at TFC!"', 'see you soon!"'),
    ('"TFC Database Backup', '"SmartPOS Database Backup')
]

replace_in_file(r"c:\Users\LENOVO\Desktop\App\Tfc_App\TFC_billing\tfc_billing.py", replacements)
try:
    replace_in_file(r"c:\Users\LENOVO\Desktop\App\Tfc_App\TFC_billing\firestore_sqlite_bridge.py", replacements)
except Exception:
    pass
try:
    replace_in_file(r"c:\Users\LENOVO\Desktop\App\Tfc_App\TFC_billing\tfc_pos_setup.iss", replacements)
except Exception:
    pass
