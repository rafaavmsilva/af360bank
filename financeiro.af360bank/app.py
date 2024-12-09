from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app, session
from datetime import datetime, timedelta
import sqlite3
import os
import pandas as pd
from werkzeug.utils import secure_filename
import sys
import uuid

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from read_excel import process_excel_file
from functools import wraps
import time
import requests
from requests.adapters import HTTPAdapter

# Create blueprint
app = Blueprint('financeiro', __name__, 
                template_folder='templates',
                static_folder='static',
                static_url_path='/financeiro/static')

def configure(main_app):
    """Configure this module with the main app's settings"""
    global app
    app.config = main_app.config
    return app

def init_session():
    """Initialize session data structures"""
    if 'upload_progress' not in session:
        session['upload_progress'] = {}
    if 'dados' not in session:
        session['dados'] = []

@app.route('/')
def index():
    """Handle the main page."""
    init_session()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Handle file upload."""
    init_session()
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nenhum arquivo selecionado'})
    
    if not file.filename.endswith('.xlsx'):
        return jsonify({'success': False, 'message': 'Formato de arquivo inválido. Use Excel (.xlsx)'})
    
    try:
        # Generate unique process ID
        process_id = str(uuid.uuid4())
        session['upload_progress'][process_id] = {
            'progress': 0,
            'message': 'Iniciando processamento...',
            'error': None
        }
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Start processing in background (simulated here)
        session['upload_progress'][process_id]['progress'] = 50
        session['upload_progress'][process_id]['message'] = 'Processando arquivo...'
        
        # Process the file
        result = process_excel_file(file_path)
        if result:
            session['upload_progress'][process_id]['progress'] = 100
            session['upload_progress'][process_id]['message'] = 'Processamento concluído!'
            return jsonify({'success': True, 'processId': process_id})
        else:
            session['upload_progress'][process_id]['error'] = 'Erro ao processar arquivo'
            return jsonify({'success': False, 'message': 'Erro ao processar arquivo'})
            
    except Exception as e:
        if process_id in session['upload_progress']:
            session['upload_progress'][process_id]['error'] = str(e)
        return jsonify({'success': False, 'message': f'Erro ao processar arquivo: {str(e)}'})

@app.route('/progress/<process_id>')
def progress(process_id):
    """Get progress of file processing."""
    init_session()
    
    if process_id not in session['upload_progress']:
        return jsonify({'error': 'Processo não encontrado'})
    
    progress_data = session['upload_progress'][process_id]
    return jsonify({
        'progress': progress_data['progress'],
        'message': progress_data['message'],
        'error': progress_data['error']
    })

@app.route('/dados')
def dados():
    """Display processed data."""
    init_session()
    return render_template('dados.html', dados=session.get('dados', []))
