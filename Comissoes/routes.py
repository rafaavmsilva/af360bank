from flask import Blueprint, render_template

comissoes_blueprint = Blueprint('comissoes', __name__)

@comissoes_blueprint.route('/')
def index():
    return render_template('comissoes/index.html')
