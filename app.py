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
            with app.app_context():
                return module.configure(app)
        return None

    def import_module_from_file(module_name, file_path):
        """Import module from file"""
        if not os.path.exists(file_path):
            print(f"Warning: Module file not found: {file_path}")
            return None
            
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None:
                print(f"Warning: Could not create spec for module: {module_name}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"Error importing module {module_name}: {str(e)}")
            return None

    # Import blueprints
    comissoes_path = os.path.join(project_root, 'Comissoes.af360bank', 'app.py')
    financeiro_path = os.path.join(project_root, 'financeiro.af360bank', 'app.py')

    print(f"Loading Comissoes module from: {comissoes_path}")
    comissoes = import_module_from_file('comissoes', comissoes_path)
    
    print(f"Loading Financeiro module from: {financeiro_path}")
    financeiro = import_module_from_file('financeiro', financeiro_path)

    # Configure and register blueprints
    if comissoes:
        comissoes_bp = configure_module(comissoes)
        if comissoes_bp:
            print("Registering Comissoes blueprint")
            app.register_blueprint(comissoes_bp, url_prefix='/comissoes')
        else:
            print("Warning: Could not configure Comissoes blueprint")
    else:
        print("Warning: Could not import Comissoes module")

    if financeiro:
        financeiro_bp = configure_module(financeiro)
        if financeiro_bp:
            print("Registering Financeiro blueprint")
            app.register_blueprint(financeiro_bp, url_prefix='/financeiro')
        else:
            print("Warning: Could not configure Financeiro blueprint")
    else:
        print("Warning: Could not import Financeiro module")

    # Add redirect routes
    @app.route('/redirect/<project>')
    def redirect_to_subdomain(project):
        if project == 'comissoes':
            return redirect('https://sistema-de-comissoes.onrender.com')
        elif project == 'financeiro':
            return redirect('https://projeto-financeiro.onrender.com')
        return redirect('/')

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
