from flask import Flask, render_template, redirect, url_for, Blueprint
import os
import sys
from flask_session import Session
import importlib.util

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'development_key')

# Configure session and app
app.config.update(
    SESSION_TYPE='filesystem',
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800,  # 30 minutes
    SESSION_REFRESH_EACH_REQUEST=True,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
    STATIC_FOLDER='static',
    TEMPLATE_FOLDER='templates'
)

# Initialize Flask-Session
Session(app)

# Function to import module from file
def import_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Import blueprints
comissoes_path = os.path.join(project_root, 'Comissoes.af360bank', 'app.py')
financeiro_path = os.path.join(project_root, 'financeiro.af360bank', 'app.py')

comissoes_module = import_module_from_file('comissoes_module', comissoes_path)
financeiro_module = import_module_from_file('financeiro_module', financeiro_path)

comissoes_blueprint = comissoes_module.app
financeiro_blueprint = financeiro_module.app

# Register blueprints
app.register_blueprint(comissoes_blueprint, url_prefix='/comissoes')
app.register_blueprint(financeiro_blueprint, url_prefix='/financeiro')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/redirect/financeiro')
def redirect_financeiro():
    """Redirect to the financeiro module."""
    return redirect(url_for('financeiro.index'))

@app.route('/redirect/comissoes')
def redirect_comissoes():
    """Redirect to the comissoes module."""
    return redirect(url_for('comissoes.index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
