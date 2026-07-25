import os
import re
import uuid
import json

base_dir = r"c:\Users\LENOVO\Desktop\App\Tfc_App\TFC_billing"

def refactor_python_file(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Special case: app_config should stay global
    content = content.replace('db.collection("app_config")', 'db.collection("app_config")') 

    # Replace db.collection('name') with db.collection('shops').document(CONFIG.get('shop_id', 'default')).collection('name')
    # Using regex to catch single and double quotes
    pattern = re.compile(r'db\.collection\(([\'"])(?!app_config|licenses|shops)(.*?)\1\)')
    new_content = pattern.sub(r'db.collection("shops").document(CONFIG.get("shop_id", "default")).collection(\1\2\1)', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Refactored Python: {filepath}")

def refactor_js_file(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # In JS, we assume SHOP_ID is defined globally (we will inject it)
    pattern = re.compile(r'db\.collection\(([\'"])(?!app_config|licenses|shops)(.*?)\1\)')
    new_content = pattern.sub(r'db.collection("shops").doc(SHOP_ID).collection(\1\2\1)', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Refactored JS: {filepath}")

# Refactor Python Files
for py_file in ["tfc_billing.py", "firestore_sqlite_bridge.py", "firestore_sync.py"]:
    refactor_python_file(os.path.join(base_dir, py_file))

# Refactor JS Files
templates_dir = os.path.join(base_dir, "templates")
if os.path.exists(templates_dir):
    for f in os.listdir(templates_dir):
        if f.endswith(".js"):
            refactor_js_file(os.path.join(templates_dir, f))

# Add UUID generation for shop_id in tfc_billing.py load_config()
tfc_billing_path = os.path.join(base_dir, "tfc_billing.py")
with open(tfc_billing_path, 'r', encoding='utf-8') as f:
    tfc_content = f.read()

config_injection = """
        # Ensure all default keys are present
        for key, value in DEFAULT_CONFIG.items():
            if key not in CONFIG:
                CONFIG[key] = value
        
        # Multi-tenant ID generation
        if 'shop_id' not in CONFIG:
            import uuid
            CONFIG['shop_id'] = str(uuid.uuid4())
            save_config()
"""
tfc_content = tfc_content.replace(
    """        # Ensure all default keys are present
        for key, value in DEFAULT_CONFIG.items():
            if key not in CONFIG:
                CONFIG[key] = value""", 
    config_injection
)

# Also ensure it imports uuid at the top if missing
if 'import uuid' not in tfc_content[:1000]:
    tfc_content = tfc_content.replace('import sys', 'import sys\nimport uuid')

with open(tfc_billing_path, 'w', encoding='utf-8') as f:
    f.write(tfc_content)
    
print("Injected shop_id logic into tfc_billing.py")
