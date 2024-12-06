from flask import Flask, render_template
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'development_key')

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Import and register blueprints
from Comissoes.af360bank.app import app as comissoes_blueprint
comissoes_blueprint.template_folder = os.path.join('Comissoes.af360bank', 'templates')
comissoes_blueprint.static_folder = os.path.join('Comissoes.af360bank', 'static')
app.register_blueprint(comissoes_blueprint, url_prefix='/comissoes')

from financeiro.af360bank.app import app as financeiro_blueprint
financeiro_blueprint.template_folder = os.path.join('financeiro.af360bank', 'templates')
financeiro_blueprint.static_folder = os.path.join('financeiro.af360bank', 'static')
app.register_blueprint(financeiro_blueprint, url_prefix='/financeiro')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
