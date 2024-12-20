@echo off
cd /d %~dp0
powershell -Command "Start-Process python 'Colorbot.py' -Verb RunAs"