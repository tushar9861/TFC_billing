import sys

file_path = r"c:\Users\LENOVO\Desktop\App\Tfc_App\TFC_billing\tfc_billing.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove firebase imports
content = content.replace("import firebase_admin\n", "")
content = content.replace("from firebase_admin import credentials\n", "")
content = content.replace("from firebase_admin import firestore\n", "")

# 2. Fix the SyncWorker firebase init
old_sync_init = """            key_path = os.path.join(os.path.expanduser('~'), "Documents", "TFC_POS", "serviceAccountKey.json")
            if not os.path.exists(key_path):
                key_path = "serviceAccountKey.json"
                if not os.path.exists(key_path):
                    self.finished.emit("Error: serviceAccountKey.json not found")
                    return
            
            if not firebase_admin._apps:
                cred = credentials.Certificate(key_path)
                firebase_admin.initialize_app(cred)
            db = firestore.client()"""
new_sync_init = "            from firestore_rest import firestore as db"
content = content.replace(old_sync_init, new_sync_init)

# 3. Fix the Global firebase init (the one that got botched)
old_global_init = """key_path = os.path.join(os.path.expanduser('~'), "Documents", "TFC_POS", "serviceAccountKey.json")
if not os.path.exists(key_path):
    key_path = "serviceAccountKey.json"

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"FAILED TO INIT FIREBASE: {e}")
    db = None"""
new_global_init = """try:
    from firestore_rest import firestore as db
except Exception as e:
    print(f"FAILED TO INIT FIREBASE: {e}")
    db = None"""
content = content.replace(old_global_init, new_global_init)

# 4. Comment out backup scheduler
old_backup = """        self.last_backup_date = None
        self.backup_scheduler = QTimer(self)
        self.backup_scheduler.timeout.connect(self.check_for_scheduled_backup)
        self.backup_scheduler.start(60000)"""
new_backup = """        # self.last_backup_date = None
        # self.backup_scheduler = QTimer(self)
        # self.backup_scheduler.timeout.connect(self.check_for_scheduled_backup)
        # self.backup_scheduler.start(60000)"""
content = content.replace(old_backup, new_backup)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("File fixed safely!")
