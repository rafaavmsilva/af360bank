from flask import Flask, render_template, redirect
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'development_key')

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Configure server name for subdomain routing
app.config['SERVER_NAME'] = 'af360bank.onrender.com'

# Import blueprints using direct path imports
from Comissoes.routes import comissoes_blueprint
from financeiro.routes import financeiro_blueprint

# Configure blueprint paths
comissoes_blueprint.template_folder = os.path.join('Comissoes', 'templates')
comissoes_blueprint.static_folder = os.path.join('Comissoes', 'static')

financeiro_blueprint.template_folder = os.path.join('financeiro', 'templates')
financeiro_blueprint.static_folder = os.path.join('financeiro', 'static')

# Register blueprints
app.register_blueprint(comissoes_blueprint, subdomain='comissoes')
app.register_blueprint(financeiro_blueprint, url_prefix='/financeiro')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
