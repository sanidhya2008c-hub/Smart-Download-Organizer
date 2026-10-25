@echo off
cd /d "%~dp0"
py -3 "%~dp0auto_sort_downloads.py"
if errorlevel 1 pause
