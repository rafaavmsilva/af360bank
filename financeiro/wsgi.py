import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from financeiro.routes import financeiro_blueprint
from flask import Flask

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'development_key')

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Configure blueprint paths
financeiro_blueprint.template_folder = os.path.join('templates')
financeiro_blueprint.static_folder = os.path.join('static')

# Register blueprint at root level since this is a standalone app
app.register_blueprint(financeiro_blueprint)

if __name__ == "__main__":
    app.run()
