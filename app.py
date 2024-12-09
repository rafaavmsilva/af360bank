from flask import Flask, render_template, redirect, url_for, Blueprint, current_app
import os
import sys
from flask_session import Session
import importlib.util

def create_app():
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

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
    )

    # Initialize Flask-Session
    Session(app)

    def configure_module(module):
        """Configure a module with app context and session"""
        if hasattr(module, 'configure'):
            return module.configure(app)
        return None

    def import_module_from_file(module_name, file_path):
        """Import module from file"""
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    # Import blueprints
    comissoes_path = os.path.join(project_root, 'Comissoes.af360bank', 'app.py')
    financeiro_path = os.path.join(project_root, 'financeiro.af360bank', 'app.py')

    comissoes = import_module_from_file('comissoes', comissoes_path)
    financeiro = import_module_from_file('financeiro', financeiro_path)

    # Configure and register blueprints
    comissoes_bp = configure_module(comissoes)
    financeiro_bp = configure_module(financeiro)

    if comissoes_bp:
        app.register_blueprint(comissoes_bp, url_prefix='/comissoes')
    if financeiro_bp:
        app.register_blueprint(financeiro_bp, url_prefix='/financeiro')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/financeiro')
    def redirect_financeiro():
        """Redirect to the financeiro module."""
        return redirect(url_for('financeiro.index'))

    @app.route('/comissoes')
    def redirect_comissoes():
        """Redirect to the comissoes module."""
        return redirect(url_for('comissoes.index'))

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
