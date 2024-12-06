from flask import Flask
from app import app as comissoes_blueprint
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'development_key')

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Register the blueprint without a prefix since this is the main app
app.register_blueprint(comissoes_blueprint)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
