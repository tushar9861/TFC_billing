import re
file_path = r"c:\Users\LENOVO\Desktop\App\Tfc_App\TFC_billing\tfc_billing.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

def replace_match(match):
    prefix = match.group(1)
    if 'import datetime' in match.group(0):
        return prefix + "import datetime\n" + prefix + "from firestore_rest import firestore as db"
    else:
        return prefix + "from firestore_rest import firestore as db"

content = re.sub(r'([ \t]+)import datetime\n[ \t]+db = firestore\.client\(\)', replace_match, content)
content = re.sub(r'([ \t]+)db = firestore\.client\(\)', replace_match, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Indentation fixed")
