; Inno Setup Script for TFC POS
; Location: C:\Users\SharpNex\Desktop\upgrade version\tfc_pos_setup.iss

[Setup]
AppName=TFC POS
AppVersion=2.6
DefaultDirName={autopf}\TFC POS
DefaultGroupName=TFC POS
UninstallDisplayIcon={app}\TFC_Billing.exe
; The following line sets the output location as requested
OutputDir=C:\Users\SharpNex\Desktop\TFC POS
OutputBaseFilename=TFC_POS_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Source paths assume PyInstaller was run with --onedir in the upgrade version folder
Source: "C:\Users\SharpNex\Desktop\upgrade version\dist\TFC_Billing\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\SharpNex\Desktop\upgrade version\config.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\TFC POS"; Filename: "{app}\TFC_Billing.exe"
Name: "{autodesktop}\TFC POS"; Filename: "{app}\TFC_Billing.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TFC_Billing.exe"; Description: "{cm:LaunchProgram,TFC POS}"; Flags: nowait postinstall skipifsilent