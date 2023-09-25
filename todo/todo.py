from flask import (
    Blueprint, flash, g, redirect, render_template, request, template_rendered, url_for
)
from werkzeug.exceptions import abort
from todo.auth import login, login_required
from todo.db import get_db

bp = Blueprint('todo', __name__, url_prefix='/todos')

@bp.route('/')
@login_required
def index():
    bd, c = get_db()
    c.execute('SELECT t.id, t.description, u.username, t.completed, t.created_at FROM todo t JOIN user u on t.created_by = u.id ORDER BY t.created_at desc')
    todos = c.fetchall()

    return render_template('todo/index.html', todos=todos)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    return ''

@bp.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    return ''