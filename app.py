from flask import Flask, redirect, render_template, request, flash, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
def configure_email():
    try:
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'rafaavmsilva3@gmail.com')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
        app.config['MAIL_DEFAULT_SENDER'] = ('AF360 Bank', os.getenv('MAIL_USERNAME', 'rafaavmsilva3@gmail.com'))
        return True
    except Exception as e:
        print(f"Error configuring email: {str(e)}")
        return False

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Token serializer
ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Application URLs configuration
APP_URLS = {
    'af360bank': 'https://af360bank.onrender.com',
    'projeto-financeiro': 'https://financeiro-af360bank.onrender.com',
    'sistema-comissoes': 'https://comissoes-af360bank.onrender.com'
}

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    name = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, default=False)
    allowed_apps = db.Column(db.String(500), default='af360bank')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def try_send_email(subject, recipient, template):
    try:
        msg = Message(subject,
                     sender=app.config['MAIL_DEFAULT_SENDER'],
                     recipients=[recipient])
        msg.html = template
        mail.send(msg)
        return True, "Email sent successfully"
    except Exception as e:
        return False, f"Email sending failed: {str(e)}"

def send_verification_email(user_email, token):
    verification_url = url_for('verify_email', token=token, _external=True)
    template = render_template('email/verify.html', verify_url=verification_url)
    return try_send_email(
        'Verificação de Email - AF360 Bank',
        user_email,
        template
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')

        # Validate email domain
        if not email.endswith('@afcredito.com.br'):
            flash('Por favor, use seu email corporativo (@afcredito.com.br)')
            return redirect(url_for('register'))

        # Validate password
        if len(password) < 8:
            flash('A senha deve ter pelo menos 8 caracteres')
            return redirect(url_for('register'))

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Este email já está registrado')
            return redirect(url_for('register'))

        # Create verification token
        token = ts.dumps(email, salt='email-verify-key')
        
        # Create new user
        new_user = User(
            email=email,
            password=generate_password_hash(password),
            name=name,
            allowed_apps='af360bank'  # Start with access only to AF360 Bank
        )
        db.session.add(new_user)
        db.session.commit()

        # Send verification email
        success, message = send_verification_email(email, token)
        if success:
            flash('Por favor, verifique seu email para ativar sua conta')
        else:
            flash('Erro ao enviar email de verificação. Por favor, contate o suporte.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/verify/<token>')
def verify_email(token):
    try:
        email = ts.loads(token, salt='email-verify-key', max_age=86400)
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_verified = True
            db.session.commit()
            flash('Email verified! You can now login.')
        else:
            flash('Invalid verification link')
    except:
        flash('The verification link has expired')
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
            
        if not user.is_verified:
            flash('Please verify your email before logging in')
            return redirect(url_for('login'))
            
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
            
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_apps = current_user.allowed_apps.split(',')
    available_apps = {
        name: url for name, url in APP_URLS.items()
        if name in user_apps
    }
    return render_template('dashboard.html', apps=available_apps)

@app.route('/authorize/<app_name>')
@login_required
def authorize_app(app_name):
    if app_name not in APP_URLS:
        flash('Application not found', 'error')
        return redirect(url_for('dashboard'))
    
    if app_name not in current_user.allowed_apps.split(','):
        flash('You do not have access to this application', 'error')
        return redirect(url_for('dashboard'))
    
    token = generate_app_token(current_user.id, app_name)
    redirect_url = f"{APP_URLS[app_name]}/auth/callback?token={token}"
    return redirect(redirect_url)

def generate_app_token(user_id, app_name):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps({'user_id': user_id, 'app': app_name})

@app.route('/api/verify_token', methods=['POST'])
def verify_token():
    token = request.json.get('token')
    app_name = request.json.get('app_name')
    
    try:
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        data = serializer.loads(token, max_age=300)
        
        if data['app'] != app_name:
            return jsonify({'valid': False, 'error': 'Invalid application'}), 400
            
        user = User.query.get(data['user_id'])
        if not user or not user.is_verified:
            return jsonify({'valid': False, 'error': 'Invalid user'}), 400
            
        return jsonify({
            'valid': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        })
    except:
        return jsonify({'valid': False, 'error': 'Invalid token'}), 400

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)