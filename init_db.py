import os
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'development'

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app import app, db

migrate = Migrate(app, db)

if __name__ == '__main__':
    from flask.cli import FlaskGroup
    cli = FlaskGroup(app)
    cli.main(['db', 'init'])
