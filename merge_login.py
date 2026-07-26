import codecs

with codecs.open('login_ui.py', 'r', 'utf-8') as f:
    login_code = f.read()

with codecs.open('tfc_billing.py', 'r', 'utf-8') as f:
    tfc_code = f.read()

import_str = "from login_ui import ModernLoginScreen, RecentAccountCard, FloatingInput"

if import_str in tfc_code:
    tfc_code = tfc_code.replace(import_str, login_code + "\n")
    with codecs.open('tfc_billing.py', 'w', 'utf-8') as f:
        f.write(tfc_code)
    print("Merged successfully!")
else:
    print("Import string not found in tfc_billing.py!")
