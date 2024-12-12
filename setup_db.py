from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(120), unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_comissoes_admin = db.Column(db.Boolean, default=False)
    is_financeiro_admin = db.Column(db.Boolean, default=False)

if __name__ == '__main__':
    # Create the migrations directory
    os.system('flask db init')
    # Create the first migration
    os.system('flask db migrate -m "Initial migration"')
    # Apply the migration
    os.system('flask db upgrade')
