@echo off
set FILE_PATH=%~dp0Colorbot.py
powershell -Command "Start-Process python '%FILE_PATH%' -Verb runAs"
