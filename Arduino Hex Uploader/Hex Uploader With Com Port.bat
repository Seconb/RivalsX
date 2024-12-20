@echo off
cd .\files
setlocal enabledelayedexpansion

echo ARDUINO UPLOADER BY SECONB (ChatGPT Helped)

:: Set a default hex file name
set hexFile=hexFile.hex

:: Check if the file exists in the current directory
if not exist "%hexFile%" (
    echo The file "%hexFile%" does not exist in the current directory.
    goto :EOF
)

:: Automatically trigger the reset for Arduino using the 1200 baud method
echo.
echo Attempting to automatically reset your Arduino...

:: Search for Arduino and reset the COM port to trigger bootloader mode
for /f "tokens=1* delims==" %%I in ('wmic path win32_pnpentity get caption  /format:list ^| find "USB Serial Device"') do (
    call :resetCOM "%%~J"
)

:: Instruct the user to wait a moment for the Arduino to reset and enter bootloader mode
echo Waiting for the Arduino to enter bootloader mode...
timeout /t 2 /nobreak >nul

:: Search for the Arduino bootloader COM port after reset
echo Searching for Arduino bootloader COM port...

for /f "tokens=1,2 delims=()" %%A in ('wmic path Win32_PnPEntity where "Name like '%%(COM%%)'" get Name /format:list ^| findstr /i "Arduino"') do (
    set "fullPort=%%B"
    goto FoundPort
)

:NoPort
echo Arduino bootloader not found. Please ensure the Arduino is in bootloader mode.
pause
exit /b

:FoundPort
:: Extract only the port number from COMx (e.g., "5" from "COM5")
set comPortNum=!fullPort:COM=!

echo Arduino bootloader found on COM!comPortNum!
echo Running avrdude with the file "%hexFile%"...

:: Execute avrdude with the chosen hex file, wrapped in quotes to handle spaces
avrdude.exe -Cavrdude.conf -v -patmega32u4 -cavr109 -PCOM!comPortNum! -b57600 -D -Uflash:w:"%hexFile%":i

:: Check if the command succeeded
if errorlevel 1 (
    echo avrdude encountered an error.
    pause
    exit /b
) else (
    echo avrdude completed successfully!
)

pause
exit /b

:: Function to trigger the bootloader reset using 1200 baud
:resetCOM <WMIC_output_line>
:: sets _COM#=line
setlocal
set "str=%~1"
set "num=%str:*(COM=%"
set "num=%num:)=%"
set port=COM%num%
echo Resetting port %port% to trigger bootloader...
mode %port%: BAUD=1200 parity=N data=8 stop=1 >nul 2>&1
goto :EOF
