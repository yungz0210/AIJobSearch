@echo off
title AI Job Search - Web Interface
cd /d "%~dp0"
echo ===================================================
echo   AI Job Search & Application Generator (Web App)
echo ===================================================
streamlit run app.py
pause
