import requests
from functools import wraps
from flask import request, redirect, session, url_for, flash

class AuthClient:
    def __init__(self, auth_server_url, app_name):
        self.auth_server_url = auth_server_url
        self.app_name = app_name

    def verify_token(self, token):
        try:
            response = requests.post(
                f"{self.auth_server_url}/api/verify_token",
                json={
                    'token': token,
                    'app_name': self.app_name
                }
            )
            return response.json() if response.ok else None
        except Exception as e:
            print(f"Error verifying token: {str(e)}")
            return None

    def login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = session.get('token')
            if not token:
                return redirect(url_for('login'))
            
            verification = self.verify_token(token)
            if not verification or not verification.get('valid'):
                session.clear()
                return redirect(url_for('login'))
            
            return f(*args, **kwargs)
        return decorated_function
