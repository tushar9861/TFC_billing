import re

file_path = r"c:\Users\LENOVO\Desktop\App\Tfc_App\TFC_billing\distributor_dashboard.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

OLD = '''class AdminLoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AdminOS \u2014 Owner Login")
        self.setFixedSize(480, 420)'''

if OLD not in content:
    print("ERROR: marker not found")
    # Try to find what's there
    idx = content.find("class AdminLoginDialog")
    print(repr(content[idx:idx+200]))
else:
    print("Found marker OK, length =", len(content))
