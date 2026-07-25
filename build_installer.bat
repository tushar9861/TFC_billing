@echo off
echo ==========================================
echo TFC POS Build System
echo ==========================================

echo [1/3] Ensuring Output Directory exists...
if not exist "C:\Users\SharpNex\Desktop\TFC POS" mkdir "C:\Users\SharpNex\Desktop\TFC POS"

echo [2/3] Bundling Application with PyInstaller...
pyinstaller --noconfirm --onedir --windowed --name "TFC_Billing" --clean "C:\Users\SharpNex\Desktop\upgrade version\tfc_billing.py"

echo.
echo [3/3] Python Bundle Complete!
echo.
echo FINAL STEP:
echo 1. Open Inno Setup Compiler.
echo 2. Open "C:\Users\SharpNex\Desktop\upgrade version\tfc_pos_setup.iss".
echo 3. Click "Build" -> "Compile" (or press F9).
echo.
echo Your installer will appear here: C:\Users\SharpNex\Desktop\TFC POS\TFC_POS_Setup.exe
pause