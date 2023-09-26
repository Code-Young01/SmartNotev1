from turtle import title
from flask import (
    Blueprint, flash, g, redirect, render_template, request, template_rendered, url_for
)
from werkzeug.exceptions import abort
from todo.auth import login, login_required
from todo.db import get_db
from datetime import datetime

bp = Blueprint('todo', __name__, url_prefix='/todos')

@bp.route('/')
@login_required
def index():
    bd, c = get_db()
    c.execute('SELECT t.id, t.title, t.description, u.username, t.completed, t.created_at FROM todo t '
              'JOIN user u on t.created_by = u.id WHERE t.deleted_at IS NULL AND t.created_by = %s ORDER BY t.created_at desc', (g.user['id'],))
    todos = c.fetchall()

    return render_template('todo/index.html', todos=todos)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        error = None

        if not title:
            error = 'Title is required.'
        elif not description:
            error = 'Description is required'
        elif not title and not description:
            error = 'Title and description is required'

        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('INSERT INTO todo (created_by, title, description, completed)'
                      'values (%s, %s, %s, %s)', (g.user['id'], title, description, False))
            db.commit()
            return redirect(url_for('todo.index'))
        
    return render_template('todo/create.html')

def get_todo(id):
    db, c = get_db()
    c.execute('SELECT t.id, t.title, t.description, t.completed, t.created_by, t.created_at, u.username '
              'FROM todo t join user u on t.created_by = u.id WHERE t.id = %s AND t.deleted_at IS NULL', (id,))
    todo = c.fetchone()

    if todo is None:
        abort(404, f"The To-Do {id} doesn't exist")

    return todo

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    todo = get_todo(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        completed = True if request.form.get('completed') == 'on' else False
        error = None

        if not title:
            error = 'Title is required'
        elif not description:
            error = 'Description is required'
        elif not title and not description:
            error = 'Title and description is required'
        
        if error is not None:
            flash(error)
        else:
            db, c = get_db()
            c.execute('UPDATE todo SET title = %s, description = %s, completed = %s, updated_at = %s'
                      ' WHERE id = %s AND created_by = %s', (title, description, completed, datetime.now(), id, g.user['id']))
            db.commit()
            return redirect(url_for('todo.index'))

    return render_template('todo/update.html', todo=todo)
    

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    db, c = get_db()
    c.execute('UPDATE todo SET deleted_at = %s WHERE id = %s AND created_by = %s', (datetime.now(), id, g.user['id']))
    db.commit()
    return redirect(url_for('todo.index'))