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
