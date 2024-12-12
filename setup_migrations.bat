@echo off
set FLASK_APP=app.py
set FLASK_ENV=development
python -m pip install flask-migrate
python -m flask db init
