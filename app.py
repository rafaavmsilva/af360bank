from flask import Flask, render_template, redirect, url_for
import os
import sys
from flask_session import Session

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'development_key')

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
Session(app)

# Import blueprints
from Comissoes.af360bank.app import app as comissoes_blueprint
from financeiro.af360bank.app import app as financeiro_blueprint

# Configure blueprint paths
comissoes_blueprint.static_folder = os.path.join('Comissoes.af360bank', 'static')
comissoes_blueprint.template_folder = os.path.join('Comissoes.af360bank', 'templates')

financeiro_blueprint.template_folder = os.path.join('financeiro.af360bank', 'templates')
financeiro_blueprint.static_folder = os.path.join('financeiro.af360bank', 'static')

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
