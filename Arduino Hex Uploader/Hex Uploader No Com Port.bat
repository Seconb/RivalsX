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

:: Instruct the user to press the reset button
echo.
echo Please press the reset button on your Arduino, wait 2 seconds, then press ENTER to begin.
pause >nul

:: Search for the Arduino bootloader COM port
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
set comPortNum=!fullPort:COM=!%

echo Arduino bootloader found on COM!comPortNum!
echo Running avrdude with the file "%hexFile%"...

:: Execute avrdude with the chosen hex file
avrdude.exe -Cavrdude.conf -v -patmega32u4 -cavr109 -PCOM!comPortNum! -b57600 -D -Uflash:w:!hexFile!:i

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
