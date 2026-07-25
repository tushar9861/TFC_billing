import sys
content = open('tfc_billing.py', 'r', encoding='utf-8').read()
content = content.replace('APP_VERSION = "1.1.0"', 'APP_VERSION = "1.1.0"\nfrom login_ui import ModernLoginScreen, RecentAccountCard, FloatingInput\n')
open('tfc_billing.py', 'w', encoding='utf-8').write(content)
