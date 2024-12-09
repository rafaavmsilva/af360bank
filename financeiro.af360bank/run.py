from flask import Flask
from app import app as financeiro_blueprint, UPLOAD_FOLDER

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.register_blueprint(financeiro_blueprint)

if __name__ == '__main__':
    print("Starting Financeiro app on http://127.0.0.1:5002/")
    app.run(host='127.0.0.1', port=5002, debug=True)
