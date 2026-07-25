import os
import re

files_to_update = [
    r"c:\Users\LENOVO\Desktop\App\Tfc_App\TFC_billing\tfc_billing.py",
    r"c:\Users\LENOVO\Desktop\App\Tfc_App\TFC_billing\firestore_sqlite_bridge.py",
    r"c:\Users\LENOVO\Desktop\App\Tfc_App\TFC_billing\firestore_sync.py"
]

for file_path in files_to_update:
    if not os.path.exists(file_path): continue
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove firebase_admin imports
    content = re.sub(r'import firebase_admin\n', '', content)
    content = re.sub(r'from firebase_admin import credentials\n', '', content)
    content = re.sub(r'from firebase_admin import firestore\n', '', content)
    
    # Replace initialization logic with our new REST client
    # In SyncWorker / FirebaseSyncWorker:
    init_pattern = r'key_path = os\.path\.join.*?\n\s*if not os\.path\.exists.*?\n\s*self\.finished\.emit.*?\n\s*return.*?\n\s*if not firebase_admin\._apps:.*?\n\s*cred = credentials\.Certificate\(key_path\).*?\n\s*firebase_admin\.initialize_app\(cred\).*?\n\s*db = firestore\.client\(\)'
    content = re.sub(init_pattern, 'from firestore_rest import firestore as db', content, flags=re.DOTALL)
    
    # In Bridge / Sync global init:
    init_pattern2 = r'try:\n\s*if not firebase_admin\._apps:.*?\n\s*cred = credentials\.Certificate\(key_path\).*?\n\s*firebase_admin\.initialize_app\(cred\).*?\n\s*db = firestore\.client\(\).*?\nexcept Exception as e:.*?\n\s*print\(f"FAILED TO INIT FIREBASE.*?:\s*\{e\}"\).*?\n\s*db = None'
    content = re.sub(init_pattern2, 'try:\n    from firestore_rest import firestore as db\nexcept Exception as e:\n    print(f"FAILED TO INIT FIREBASE: {e}")\n    db = None', content, flags=re.DOTALL)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Updated {file_path}")
