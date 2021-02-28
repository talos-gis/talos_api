#include <./iss-app_consts.iss>
#define public InOutDir "..\.."

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
WizardStyle=modern
DefaultDirName=C:\{#AppName}
DefaultGroupName={#AppName}
Compression=lzma2
SolidCompression=yes
OutputDir={#InOutDir}
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
Source: "{#InOutDir}\{#AppName}\*.*"; DestDir: "{app}\{#AppName}";                Flags: recursesubdirs; Components: app;
Source: "{#InOutDir}\{#PythonName}\*.*";  DestDir: "{app}\{#PythonName}";  Flags: recursesubdirs; Components: py;

[Run]
Filename: "{app}\{#AppName}\installer\configure.bat";  Parameters: ""; Components: config
Filename: "{app}\{#AppName}\installer\iis-deploy.bat"; Parameters: ""; Components: iis
; Filename: "{app}\{#AppName}\installer\iis-deploy-Add_Module_Mapping.png"; Components: iis

[UninstallRun]
Filename: "{app}\{#AppName}\installer\iis-undeploy.bat"; Parameters: ""; Components: iis
