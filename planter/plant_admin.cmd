@echo off

REM Define user-level install path
set INSTALL_DIR=%LOCALAPPDATA%\WizRat

REM Create the directory if it doesn't exist
if not exist %INSTALL_DIR% (
    mkdir %INSTALL_DIR%
)

REM Copy the executable
copy /Y "client.exe" "%INSTALL_DIR%\client.exe" >nul

REM Delete the scheduled task if it exists
schtasks /delete /tn "WizRat Client Startup" /f >nul 2>&1


REM Create a scheduled task to run at login (user-level)
schtasks /create ^
  /tn "WizRat Client Startup" ^
  /tr "%INSTALL_DIR%\client.exe" ^
  /sc onlogon ^
  /ru "%USERNAME%" ^
  /rl LIMITED ^
  /f


echo.
echo [INFO] WizRat client has been installed for current user at
echo [INFO] %INSTALL_DIR%
