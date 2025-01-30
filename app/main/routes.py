from . import main_bp
from flask import render_template

@main_bp.get('/')
def home():
    return render_template('index.html')

@main_bp.get('/editor')
def editor():
    return render_template('editor.html')