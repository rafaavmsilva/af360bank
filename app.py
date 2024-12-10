from flask import Flask, redirect, render_template, request, flash, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Email configuration with detailed error handling
def configure_email():
    try:
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        app.config['MAIL_USERNAME'] = 'rafaavmsilva3@gmail.com'  # Personal Gmail account
        app.config['MAIL_PASSWORD'] = 'erfbeqeyfcqcvwwl'  # App password from personal Gmail
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
login_manager.login_view = 'login'

# Token serializer for email verification
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(120), unique=True)

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
    """
    Attempt to send email using Flask-Mail
    """
    try:
        msg = Message(subject,
                     sender=('AF360 Bank', 'rafaavmsilva3@gmail.com'),
                     recipients=[recipient])
        msg.html = template
        mail.send(msg)
        print("Email sent successfully!")
        return True, "Email sent successfully"
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False, f"Email sending failed: {str(e)}"

def send_verification_email(user_email, token):
    verification_url = url_for('verify_email', token=token, _external=True)
    template = render_template('verification_email.html', verification_url=verification_url)
    
    success, message = try_send_email(
        'Verify your email',
        user_email,
        template
    )
    
    if not success:
        flash(f"Error sending verification email: {message}", 'error')
        return False
    return True

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate email domain
        if not email.endswith('@afcredito.com.br'):
            flash('Please use your @afcredito.com.br email address')
            return redirect(url_for('register'))
        
        # Check if email exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered')
            return redirect(url_for('register'))
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message)
            return redirect(url_for('register'))
        
        # Generate verification token
        token = ts.dumps(email, salt='email-verify-key')
        
        # Create new user
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            verification_token=token
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Send verification email
        send_verification_email(email, token)
        
        flash('Registration successful! Please check your email to verify your account.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/verify/<token>')
def verify_email(token):
    try:
        email = ts.loads(token, salt='email-verify-key', max_age=86400)  # 24 hour expiration
        user = User.query.filter_by(email=email).first()
        if user:
            user.email_verified = True
            user.verification_token = None
            db.session.commit()
            flash('Email verified! You can now login.')
        else:
            flash('Invalid verification link.')
    except:
        flash('Invalid or expired verification link.')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
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
            return redirect(url_for('index'))
            
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/resend_verification')
def resend_verification():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    if current_user.email_verified:
        flash('Your email is already verified')
        return redirect(url_for('index'))
    
    token = ts.dumps(current_user.email, salt='email-verify-key')
    current_user.verification_token = token
    db.session.commit()
    
    send_verification_email(current_user.email, token)
    flash('Verification email has been resent')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/redirect/<project>')
@login_required
def redirect_to_subdomain(project):
    if project == 'comissoes':
        return redirect('https://sistema-de-comissoes.onrender.com')
    elif project == 'financeiro':
        return redirect('https://projeto-financeiro.onrender.com')
    return redirect('/')

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/test_email')
def test_email():
    success, message = try_send_email(
        'Test Email from AF360 Bank',
        'rafaelaugustovianna@hotmail.com',
        '<h1>Test Email</h1><p>This is a test email from AF360 Bank.</p>'
    )
    return jsonify({'success': success, 'message': message})

# Create the database tables
def init_db():
    with app.app_context():
        # Drop all tables first
        db.drop_all()
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_db()  # Initialize the database before running the app
    app.run(debug=True)