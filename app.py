from flask import Flask, redirect, render_template, request, flash, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import os
from dotenv import load_dotenv
import re
import secrets
from datetime import datetime
from auth_client import AuthClient

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

# Initialize AuthClient with app_name
auth = AuthClient(
    app_name="AF360Bank",
    base_url=os.getenv('AUTH_BASE_URL'),
    client_id=os.getenv('AUTH_CLIENT_ID'),
    client_secret=os.getenv('AUTH_CLIENT_SECRET')
)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration with detailed error handling
def configure_email():
    try:
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        app.config['MAIL_USERNAME'] = 'rafaavmsilva3@gmail.com'
        app.config['MAIL_PASSWORD'] = 'erfbeqeyfcqcvwwl'
        app.config['MAIL_DEFAULT_SENDER'] = ('AF360 Bank', 'rafaavmsilva3@gmail.com')
        app.config['MAIL_MAX_EMAILS'] = None
        app.config['MAIL_ASCII_ATTACHMENTS'] = False
        
        return True
    except Exception as e:
        print(f"Error configuring email: {str(e)}")
        return False

# Configure email
if not configure_email():
    print("Warning: Email configuration failed!")

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the login view

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(120), unique=True)

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"

def try_send_email(subject, recipient, template):
    try:
        msg = Message(
            subject,
            recipients=[recipient],
            html=template
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_verification_email(user_email, token):
    verification_url = url_for('verify_email', token=token, _external=True)
    template = render_template(
        'verification_email.html',
        verification_url=verification_url
    )
    
    if try_send_email("Verify your email", user_email, template):
        flash('Verification email sent! Please check your inbox.')
    else:
        flash('Error sending verification email. Please try again later.')

def generate_redirect_token(destination):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps({'destination': destination, 'timestamp': str(datetime.utcnow())})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Basic validation
        if not email or not password:
            flash('All fields are required')
            return redirect(url_for('register'))

        # Password validation
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message)
            return redirect(url_for('register'))

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered')
            return redirect(url_for('register'))

        # Create new user
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        verification_token = serializer.dumps(email, salt='email-verification')
        
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            verification_token=verification_token
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            send_verification_email(email, verification_token)
            flash('Registration successful! Please check your email to verify your account.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Error during registration. Please try again.')
            print(f"Registration error: {str(e)}")
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/verify/<token>')
def verify_email(token):
    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='email-verification', max_age=3600)
        user = User.query.filter_by(email=email).first()
        
        if user:
            user.email_verified = True
            user.verification_token = None
            db.session.commit()
            flash('Email verified successfully! You can now log in.')
        else:
            flash('Invalid verification token')
    except Exception as e:
        flash('Invalid or expired verification token')
        print(f"Verification error: {str(e)}")
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Invalid email or password')
            return redirect(url_for('login'))
            
        if not user.email_verified:
            flash('Please verify your email before logging in')
            return redirect(url_for('login'))
            
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
            
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user and not user.email_verified:
            serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            verification_token = serializer.dumps(email, salt='email-verification')
            
            user.verification_token = verification_token
            db.session.commit()
            
            send_verification_email(email, verification_token)
            flash('Verification email resent! Please check your inbox.')
        else:
            flash('Invalid email or account already verified')
            
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/redirect/<project>')
@login_required
def redirect_to_project(project):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
        
    if project == 'comissoes':
        token = generate_redirect_token('comissoes')
        return redirect(f'https://sistema-de-comissoes.onrender.com/auth?token={token}')
    elif project == 'financeiro':
        token = generate_redirect_token('financeiro')
        return redirect(f'https://financeiro-af360bank.onrender.com/auth?token={token}')
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/test-email')
def test_email():
    if try_send_email(
        "Test Email",
        "rafaavmsilva3@gmail.com",
        "<h1>Test Email</h1><p>This is a test email from AF360 Bank.</p>"
    ):
        return "Email sent successfully!"
    return "Error sending email"

# Create the database tables
def init_db():
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")

if __name__ == '__main__':
    # Force HTTPS
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    
    # Set session cookie settings
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    init_db()  # Initialize the database before running the app
    app.run(debug=True, ssl_context='adhoc')