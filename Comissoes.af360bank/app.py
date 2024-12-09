from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
import pandas as pd
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional
import os
from werkzeug.utils import secure_filename
import logging
from logging.handlers import RotatingFileHandler
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import imgkit
from datetime import datetime

# Create blueprint
app = Blueprint('comissoes', __name__, 
                template_folder='templates',
                static_folder='static',
                static_url_path='/comissoes/static')

def configure(main_app):
    """Configure this module with the main app's settings"""
    global app
    app.config = main_app.config
    return app

# Ensure session is initialized with required data structures
def init_session():
    if 'dados' not in session:
        session['dados'] = []
    if 'comissoes' not in session:
        session['comissoes'] = []
    if 'tabela_config' not in session:
        session['tabela_config'] = {
            'tabela1': {'tipo': 'porcentagem', 'faixas': []},
            'tabela2': {'tipo': 'porcentagem', 'faixas': []},
            'tabela3': {'tipo': 'fixo', 'faixas': []}
        }

def is_valid_file(filename: str) -> bool:
    """Validate if the file is a CSV or Excel file."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

def read_file(file):
    """Read CSV or Excel file into a pandas DataFrame."""
    filename = secure_filename(file.filename)
    if filename.endswith('.csv'):
        return pd.read_csv(file, encoding='utf-8')
    else:
        return pd.read_excel(file)

def convert_to_float(value: str) -> float:
    """Convert a Brazilian currency string to float."""
    try:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove R$, spaces, and replace comma with dot
            value = value.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(value)
        return 0.0
    except (ValueError, InvalidOperation):
        return 0.0

def format_currency(value: any) -> str:
    """Format a number as Brazilian currency."""
    try:
        return f"R$ {float(value):,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    except (ValueError, TypeError):
        return "R$ 0,00"

@app.route('/')
def index():
    """Handle the main page and file upload."""
    init_session()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Handle file upload."""
    init_session()
    if 'file' not in request.files:
        flash('Nenhum arquivo selecionado')
        return redirect(url_for('comissoes.index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado')
        return redirect(url_for('comissoes.index'))
    
    if not is_valid_file(file.filename):
        flash('Formato de arquivo inválido. Use CSV ou Excel.')
        return redirect(url_for('comissoes.index'))
    
    try:
        df = read_file(file)
        dados = df.to_dict('records')
        session['dados'] = dados
        return redirect(url_for('comissoes.dados'))
    except Exception as e:
        flash(f'Erro ao processar arquivo: {str(e)}')
        return redirect(url_for('comissoes.index'))

@app.route('/dados')
def dados():
    """Display uploaded data."""
    init_session()
    if 'dados' not in session or not session['dados']:
        flash('Nenhum dado carregado')
        return redirect(url_for('comissoes.index'))
    return render_template('dados.html', dados=session['dados'])

@app.route('/comissoes')
def comissoes():
    """Calculate and display commissions."""
    init_session()
    if 'dados' not in session or not session['dados']:
        flash('Nenhum dado carregado')
        return redirect(url_for('comissoes.index'))
    return render_template('comissoes.html', dados=session['dados'])
