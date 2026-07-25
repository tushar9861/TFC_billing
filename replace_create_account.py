file_path = r"c:\Users\LENOVO\Desktop\App\Tfc_App\TFC_billing\tfc_billing.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

with open("saved_create_account.py", "r", encoding="utf-8") as f:
    new_create_account = f.read()

start_str = "    def create_account(self):"
end_str = "# ================================\n# LOGIN SCREEN"

start_idx = content.find(start_str)
end_idx = content.find(end_str, start_idx)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_create_account + "\n" + content[end_idx:]
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("create_account patched successfully")
else:
    print("Could not find the block to replace!")
