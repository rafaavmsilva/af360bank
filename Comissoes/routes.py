from flask import render_template
from . import comissoes_blueprint

@comissoes_blueprint.route('/')
def index():
    return render_template('comissoes/index.html')
