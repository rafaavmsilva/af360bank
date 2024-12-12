@echo off
cd "c:/Users/marke/OneDrive/Área de Trabalho/Menu com login/af360bank"
set PYTHONPATH=%cd%
set FLASK_APP=app.py
"c:\users\marke\appdata\local\programs\python\python39\python.exe" -m flask db init
