#define MyAppName "Iyrin"
#ifndef MyAppVersion
  #define MyAppVersion "0.2.0"
#endif

[Setup]
AppId={{639EC77E-57FF-471D-87B4-113F338940F5}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=is-leeroy-jenkins
DefaultDirName={localappdata}\Programs\Iyrin
DefaultGroupName=Iyrin
OutputDir=..\dist-installer
OutputBaseFilename=Iyrin-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
WizardStyle=modern
UninstallDisplayName=Iyrin
UninstallDisplayIcon={app}\Iyrin.exe
CloseApplications=yes

[Files]
Source: "..\dist\Iyrin\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Icons]
Name: "{group}\Iyrin"; Filename: "{app}\Iyrin.exe"
Name: "{autodesktop}\Iyrin"; Filename: "{app}\Iyrin.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Iyrin.exe"; Description: "Launch Iyrin"; Flags: nowait postinstall skipifsilent
