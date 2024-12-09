from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from datetime import datetime, timedelta
import sqlite3
import os
import pandas as pd
from werkzeug.utils import secure_filename
import sys

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
