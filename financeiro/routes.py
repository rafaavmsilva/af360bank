from flask import Blueprint, render_template

financeiro_blueprint = Blueprint('financeiro', __name__)

@financeiro_blueprint.route('/')
def index():
    return render_template('financeiro/index.html')
