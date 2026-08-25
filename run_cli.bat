@echo off
title AI Job Search - CLI
cd /d "%~dp0"
echo ===================================================
echo   AI Job Search & Application Generator (CLI)
echo ===================================================
python main.py --resume "Chin Yung Wei Resume - Aug 2026.docx" --job "test_job.txt"
pause
