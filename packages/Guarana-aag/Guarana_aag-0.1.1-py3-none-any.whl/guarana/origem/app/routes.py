from flask import render_template

from app import app
from .config import *


@app.route('/')
def index():
    return render_template(
        'index.html',
        titulo=TITULO,
        estilo = ESTILO
    )

@app.route('/login')
def login():
    return render_template(
        'login.html',
        titulo=TITULO,
        estilo = ESTILO
    )
