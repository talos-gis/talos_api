#include <./iss-app_consts.iss>

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
WizardStyle=modern
DefaultDirName=C:\{#AppName}
DefaultGroupName={#AppName}
Compression=lzma2
SolidCompression=yes
OutputDir=.\
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Types]
Name: "full";       Description: "App Installation + Python + IIS Deployment";
Name: "app_py";     Description: "App Installation + Python";
Name: "custom";     Description: "Custom Installation";       Flags: iscustom;

[Components]
Name: py;     Description: Python {#PythonVersion} Installation;          Types: full app_py custom;
Name: app;    Description: {#AppName} Installation;           Types: full app_py custom;
Name: config; Description: {#AppName} Configuration;          Types: full app_py custom;
Name: iis;    Description: IIS Deployment;                    Types: full custom;

[Files]
Source: "d:\iss\{#AppName}\*.*"; DestDir: "{app}\app";                Flags: recursesubdirs; Components: app;
Source: "d:\iss\{#PythonName}\*.*";  DestDir: "{app}\{#PythonName}";  Flags: recursesubdirs; Components: py;

[Run]
Filename: "{app}\app\installer\configure.bat";  Parameters: ""; Components: config
Filename: "{app}\app\installer\iis-deploy.bat"; Parameters: ""; Components: iis
; Filename: "{app}\app\installer\iis-deploy-Add_Module_Mapping.png"; Components: iis

[UninstallRun]
Filename: "{app}\app\installer\iis-undeploy.bat"; Parameters: ""; Components: iis
