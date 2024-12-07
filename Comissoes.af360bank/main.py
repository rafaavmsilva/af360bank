from flask import Flask
from app import *

if __name__ == '__main__':
    # Ensure the app is configured as a standalone application
    if isinstance(app, Blueprint):
        flask_app = Flask(__name__)
        flask_app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'development_key')
        flask_app.config.update(
            SESSION_TYPE='filesystem',
            SESSION_COOKIE_SECURE=False,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
        )
        Session(flask_app)
        flask_app.register_blueprint(app)
        app = flask_app

    app.run(host='127.0.0.1', port=5001, debug=True)
