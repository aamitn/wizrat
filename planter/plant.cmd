@echo off

REM Define paths
set "INSTALL_DIR=%LOCALAPPDATA%\WizRat"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "EXE_NAME=client.exe"
set "EXE_PATH=%INSTALL_DIR%\%EXE_NAME%"
set "SHORTCUT_PATH=%STARTUP_DIR%\WizRat.lnk"

REM Create install directory if needed
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

REM Copy client.exe to install location
copy /Y "%EXE_NAME%" "%EXE_PATH%" >nul

REM Create shortcut using PowerShell
powershell -Command ^
"$WshShell = New-Object -ComObject WScript.Shell; ^
$Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); ^
$Shortcut.TargetPath = '%EXE_PATH%'; ^
$Shortcut.WorkingDirectory = '%INSTALL_DIR%'; ^
$Shortcut.WindowStyle = 7; ^
$Shortcut.Description = 'WizRat Client Auto Start'; ^
$Shortcut.Save()"

echo.
echo [INFO] WizRat client installed to: %EXE_PATH%
echo [INFO] Startup shortcut created at: %SHORTCUT_PATH%
