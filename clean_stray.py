file_path = r"c:\Users\LENOVO\Desktop\App\Tfc_App\TFC_billing\tfc_billing.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

stray_block = """
        
        self.license_key = QLineEdit()
        self.license_key.setPlaceholderText("License Key (Required for Cloud Sync)")
        layout.addWidget(self.license_key)
        
"""

# Replace all occurrences EXCEPT the one in FirstTimeSetupScreen
# Actually, FirstTimeSetupScreen has it properly indented or placed. Let's just remove ALL stray_blocks
# and make sure FirstTimeSetupScreen still has it.

content = content.replace(stray_block, "")

# Ensure FirstTimeSetupScreen has it (patch_setup_ui.py placed it cleanly as:
#         self.license_key = QLineEdit()
#         self.license_key.setPlaceholderText("License Key (Required for Cloud Sync)")
#         layout.addWidget(self.license_key)
# Without the huge spaces around it.

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Cleaned up stray license key fields.")
