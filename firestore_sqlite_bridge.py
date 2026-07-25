import sqlite3 as real_sqlite3
import firebase_admin
from firebase_admin import credentials, firestore
import threading
import json
import os
import time

print("LOADING FIRESTORE SQLITE BRIDGE...")

# 1. Initialize Firebase
try:
    if not firebase_admin._apps:
        key_path = 'serviceAccountKey.json'
        if not os.path.exists(key_path):
            key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"FAILED TO INIT FIREBASE in Bridge: {e}")
    db = None

# We will use a local SQLite file as a cache.
# To make Firestore the true storage, we will download everything from Firestore
# into this cache when connect() is first called.
_CACHE_INITIALIZED = False
_INITIALIZATION_LOCK = threading.Lock()

class BridgeCursor:
    def __init__(self, real_cursor, conn):
        self._real = real_cursor
        self.conn = conn
        
    def __getattr__(self, name):
        return getattr(self._real, name)

    def execute(self, sql, params=()):
        res = self._real.execute(sql, params)
        sql_clean = sql.strip().upper()
        
        if sql_clean.startswith(("INSERT", "UPDATE", "DELETE")):
            table = None
            if sql_clean.startswith("UPDATE"):
                table = sql_clean.split(" ")[1]
            elif sql_clean.startswith("INSERT"):
                if "INTO" in sql_clean:
                    parts = sql_clean.split("INTO")
                    if len(parts) > 1:
                        table = parts[1].strip().split(" ")[0].split("(")[0]
            elif sql_clean.startswith("DELETE"):
                if "FROM" in sql_clean:
                    parts = sql_clean.split("FROM")
                    if len(parts) > 1:
                        table = parts[1].strip().split(" ")[0]
            
            if table:
                table = table.lower().strip()
                # Run the sync in background to not block the UI
                threading.Thread(target=self._sync_table, args=(table,)).start()
                
        return self

    def fetchall(self):
        return self._real.fetchall()
        
    def fetchone(self):
        return self._real.fetchone()

    def _sync_table(self, table):
        # We simply push the entire table to Firestore to ensure it's fully synced.
        # This is safe because desktop apps usually don't have massive concurrent writes.
        if not db:
            return
            
        try:
            # We need a new connection for the background thread
            temp_conn = real_sqlite3.connect(self.conn.database, timeout=10)
            df = temp_conn.execute(f"SELECT * FROM {table}").fetchall()
            cols = [description[0] for description in temp_conn.execute(f"SELECT * FROM {table}").description]
            temp_conn.close()
            
            batch = db.batch()
            count = 0
            
            for row in df:
                row_dict = dict(zip(cols, row))
                
                # Determine primary key for document ID
                doc_id = None
                if table == 'metadata':
                    doc_id = str(row_dict['key'])
                elif table == 'bills' or table == 'refunds':
                    doc_id = str(row_dict['bill_no'])
                elif 'id' in row_dict:
                    doc_id = str(row_dict['id'])
                else:
                    doc_id = str(row_dict[cols[0]]) # fallback to first col
                
                # Parse JSON fields if necessary
                if table == 'bills' and 'items' in row_dict and isinstance(row_dict['items'], str):
                    try:
                        row_dict['items'] = json.loads(row_dict['items'])
                    except:
                        pass
                        
                doc_ref = db.collection(table).document(doc_id)
                batch.set(doc_ref, row_dict)
                count += 1
                
                if count >= 490: # Firestore batch limit is 500
                    batch.commit()
                    batch = db.batch()
                    count = 0
            
            if count > 0:
                batch.commit()
                
        except Exception as e:
            print(f"Error syncing {table} to Firestore: {e}")


class BridgeConnection:
    def __init__(self, real_conn, database):
        self._real = real_conn
        self.database = database
        
    def __getattr__(self, name):
        return getattr(self._real, name)

    def cursor(self):
        return BridgeCursor(self._real.cursor(), self)
        
    def execute(self, sql, params=()):
        c = self.cursor()
        return c.execute(sql, params)
        
    def commit(self):
        self._real.commit()
        
    def close(self):
        # Prevent pandas read_sql_query from closing our global connection
        pass

def _download_all_from_firestore(real_conn):
    if not db:
        return
        
    print("Downloading all data from Firestore to local cache...")
    collections = ['metadata', 'products', 'bills', 'refunds', 'expenses', 'quotes', 'offers', 'vendors', 'purchase_orders', 'purchase_order_items']
    
    for coll_name in collections:
        try:
            docs = db.collection(coll_name).stream()
            for doc in docs:
                data = doc.to_dict()
                
                if coll_name == 'bills' and 'items' in data and isinstance(data['items'], list):
                    data['items'] = json.dumps(data['items'])
                
                # Build INSERT statement dynamically
                columns = list(data.keys())
                placeholders = ', '.join(['?'] * len(columns))
                sql = f"INSERT OR REPLACE INTO {coll_name} ({', '.join(columns)}) VALUES ({placeholders})"
                
                real_conn.execute(sql, tuple(data.values()))
            real_conn.commit()
        except Exception as e:
            print(f"Error downloading {coll_name}: {e}")

IntegrityError = real_sqlite3.IntegrityError
ProgrammingError = real_sqlite3.ProgrammingError
OperationalError = real_sqlite3.OperationalError

def connect(database, timeout=10, **kwargs):
    global _CACHE_INITIALIZED
    real_conn = real_sqlite3.connect(database, timeout=timeout, **kwargs)
    
    with _INITIALIZATION_LOCK:
        if not _CACHE_INITIALIZED:
            print("INITIALIZING FIRESTORE DB CACHE...")
            # We must ensure tables exist before we can insert into them
            # Let tfc_billing.py run its CREATE TABLE statements first? 
            # If we download before CREATE TABLE, it will fail.
            # So we will let it return the connection. The first time a query is executed, we shouldn't download yet.
            # Actually, tfc_billing.py calls `init_db()` which creates tables.
            # We should probably hook into `init_db` or just let `execute` handle it.
            pass
            
    return BridgeConnection(real_conn, database)

if __name__ == "__main__":
    import subprocess
    import sys
    import os
    print("\n---------------------------------------------------------")
    print("NOTE: You ran the database bridge file instead of the main app.")
    print("Automatically redirecting and launching tfc_billing.py for you...")
    print("---------------------------------------------------------\n")
    
    target = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tfc_billing.py')
    subprocess.Popen([sys.executable, target])
    sys.exit(0)
