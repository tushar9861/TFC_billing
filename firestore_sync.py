import sqlite3 as real_sqlite3
import threading
import json
import os
import datetime
import traceback

print("INITIALIZING FIRESTORE SYNC MODULE...")

# Initialize Firebase
try:
    from firestore_rest import firestore as db
except Exception as e:
    print(f"FAILED TO INIT FIREBASE: {e}")
    db = None

class SyncCursor:
    def __init__(self, real_cursor, conn):
        self._real = real_cursor
        self.conn = conn

    def __getattr__(self, name):
        return getattr(self._real, name)

    def execute(self, sql, params=()):
        res = self._real.execute(sql, params)
        sql_clean = sql.strip().upper()
        
        # If it's a modification query, we push it to the sync queue
        if sql_clean.startswith(("INSERT", "UPDATE", "DELETE")):
            # Get table name
            # Very basic extraction: UPDATE table SET ..., INSERT INTO table (...) ..., DELETE FROM table WHERE ...
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
                # Run the sync in background
                threading.Thread(target=self._sync_to_firestore, args=(table, sql, params, self._real.lastrowid)).start()
                
        return res

    def _sync_to_firestore(self, table, sql, params, lastrowid):
        if not db:
            return
        
        try:
            sql_clean = sql.strip().upper()
            
            # Since we can't easily reverse engineer every UPDATE/DELETE without writing a full SQL parser,
            # and because this is a desktop app with low write volume, a very robust approach is to 
            # re-fetch the affected record from the local SQLite DB and OVERWRITE it in Firestore.
            
            doc_id = None
            doc_data = None
            is_delete = sql_clean.startswith("DELETE")
            
            # Determine the ID of the affected record based on the query pattern
            if table == "metadata":
                if is_delete:
                    doc_id = params[0]
                else:
                    doc_id = params[0] # INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)
                    doc_data = {'value': str(params[1])}
                    
            elif table == "products":
                if sql_clean.startswith("INSERT"):
                    doc_id = str(lastrowid)
                elif sql_clean.startswith("UPDATE"):
                    # WHERE id = ? or WHERE name = ? AND inventory_type = ?
                    # It's easier to just re-sync the entire products collection, or find the ID
                    if "WHERE ID =" in sql_clean or "WHERE ID=?" in sql_clean:
                        doc_id = str(params[-1])
                    else:
                        # Find by name and inventory_type
                        # UPDATE products SET qty = qty - ? WHERE name = ? AND inventory_type = ?
                        name = params[1]
                        inv_type = params[2]
                        real_c = self.conn._real.cursor()
                        real_c.execute("SELECT id FROM products WHERE name=? AND inventory_type=?", (name, inv_type))
                        row = real_c.fetchone()
                        if row:
                            doc_id = str(row[0])
                elif sql_clean.startswith("DELETE"):
                    if "WHERE ID =" in sql_clean or "WHERE ID=?" in sql_clean:
                        doc_id = str(params[0])
                    else:
                        name = params[0]
                        # Too late to get ID if it's already deleted locally! 
                        # We should have intercepted before execute.
                        # Wait, for deletions, it's safer to just sync everything or keep track.
            
            # For this MVP Sync adapter, we will just sync the ENTIRE TABLE to Firestore 
            # if it's small, OR we can implement the full SQLite -> Firestore mirror logic.
            # Actually, a much safer approach: 
            # Write a `sync_table(table_name)` function that overwrites Firestore with the current SQLite state.
            
            self._full_table_sync(table)
            
        except Exception as e:
            print(f"Error syncing {table} to Firestore: {e}")
            traceback.print_exc()

    def _full_table_sync(self, table):
        # To avoid massive network I/O, we only sync the affected row if we can.
        # But `sync_table` is bulletproof for small tables.
        pass

class SyncConnection:
    def __init__(self, real_conn):
        self._real = real_conn

    def __getattr__(self, name):
        return getattr(self._real, name)

    def cursor(self):
        return SyncCursor(self._real.cursor(), self)
        
    def execute(self, sql, params=()):
        c = self.cursor()
        return c.execute(sql, params)

def connect(database, timeout=10, **kwargs):
    real_conn = real_sqlite3.connect(database, timeout=timeout, **kwargs)
    return SyncConnection(real_conn)
    
def initial_download_from_firestore(db_file):
    # This will be called ONCE at application startup.
    # It will download ALL data from Firestore and populate the local SQLite DB.
    pass
