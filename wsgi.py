import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from flask import Flask, request
from Comissoes.routes import comissoes_blueprint
from financeiro.routes import financeiro_blueprint

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'development_key')

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Configure blueprint paths
comissoes_blueprint.template_folder = os.path.join('Comissoes', 'templates')
comissoes_blueprint.static_folder = os.path.join('Comissoes', 'static')

financeiro_blueprint.template_folder = os.path.join('financeiro', 'templates')
financeiro_blueprint.static_folder = os.path.join('financeiro', 'static')

@app.before_request
def before_request():
    host = request.host.split(':')[0]
    if host.startswith('comissoes.'):
        # Remove other blueprints if registered
        app.blueprints = {}
        app.register_blueprint(comissoes_blueprint)
    elif host.startswith('financeiro.'):
        # Remove other blueprints if registered
        app.blueprints = {}
        app.register_blueprint(financeiro_blueprint)
    else:
        # Main application - register all blueprints
        app.register_blueprint(comissoes_blueprint, url_prefix='/comissoes')
        app.register_blueprint(financeiro_blueprint, url_prefix='/financeiro')

if __name__ == "__main__":
    app.run()
