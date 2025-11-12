[Setup]
AppName=Dr. Tauseef's Derivation Helper
AppVersion=1.0
AppPublisher=Dr. Syed Tauseef
DefaultDirName={autopf}\Dr_Tauseefs_Derivation_Helper
DefaultGroupName=Dr. Tauseef's Derivation Helper
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkablealone

[Files]
Source: "dist\laplace*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; This line tells Inno Setup to grab everything from the 'dist/laplace' folder
; (which PyInstaller makes) and put it in the installation directory.

[Icons]
Name: "{group}\Dr. Tauseef's Derivation Helper"; Filename: "{app}\laplace.exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\Dr. Tauseef's Derivation Helper"; Filename: "{app}\laplace.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\laplace.exe"; Description: "{cm:LaunchProgram,Dr. Tauseef's Derivation Helper}"; Flags: nowait postinstall skipifsilent