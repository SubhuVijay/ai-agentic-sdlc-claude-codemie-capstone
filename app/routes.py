from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Entry

TITLE_MAX = 64
DESCRIPTION_MAX = 120

def read_entry_form(form):
    values = {
        'title': (form.get('title') or '').strip(),
        'description': (form.get('description') or '').strip(),
    }
    errors = {}
    if not values['title']:
        errors['title'] = 'Title is required.'
    elif len(values['title']) > TITLE_MAX:
        errors['title'] = 'Title must be %d characters or fewer.' % TITLE_MAX
    if not values['description']:
        errors['description'] = 'Description is required.'
    elif len(values['description']) > DESCRIPTION_MAX:
        errors['description'] = 'Description must be %d characters or fewer.' % DESCRIPTION_MAX
    return values, errors

@app.route('/')
def index():
    entries = Entry.query.order_by(Entry.id).all()
    return render_template('index.html', entries=entries)

@app.route('/index')
def index_alias():
    return redirect(url_for('index'))

@app.route('/entries/new')
def new_entry():
    return render_template('entry_form.html', heading='Create entry', submit_label='Create',
                           form_action=url_for('create_entry'), values={}, errors={})

@app.route('/entries', methods=['POST'])
def create_entry():
    values, errors = read_entry_form(request.form)
    if errors:
        return render_template('entry_form.html', heading='Create entry', submit_label='Create',
                               form_action=url_for('create_entry'), values=values, errors=errors)
    db.session.add(Entry(title=values['title'], description=values['description']))
    db.session.commit()
    flash('Entry created.', 'success')
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add():
    return redirect(url_for('create_entry'), code=307)

@app.route('/entries/<int:id>/edit')
def edit_entry(id):
    entry = Entry.query.get_or_404(id)
    return render_template('entry_form.html', heading='Edit entry', submit_label='Update',
                           form_action=url_for('update_entry', id=entry.id),
                           values={'title': entry.title, 'description': entry.description}, errors={})

@app.route('/entries/<int:id>', methods=['POST'])
def update_entry(id):
    entry = Entry.query.get_or_404(id)
    values, errors = read_entry_form(request.form)
    if errors:
        return render_template('entry_form.html', heading='Edit entry', submit_label='Update',
                               form_action=url_for('update_entry', id=entry.id), values=values, errors=errors)
    entry.title = values['title']
    entry.description = values['description']
    db.session.commit()
    flash('Entry updated.', 'success')
    return redirect(url_for('index'))

@app.route('/update/<int:id>')
def updateRoute(id):
    return redirect(url_for('edit_entry', id=id))

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    return redirect(url_for('update_entry', id=id), code=307)

@app.route('/entries/<int:id>/delete')
def confirm_delete_entry(id):
    entry = Entry.query.get_or_404(id)
    return render_template('entry_delete_confirm.html', entry=entry)

@app.route('/entries/<int:id>/delete', methods=['POST'])
def delete_entry(id):
    entry = Entry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    flash('Entry deleted.', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    return redirect(url_for('confirm_delete_entry', id=id))

@app.route('/entries/<int:id>/toggle', methods=['POST'])
def toggle_entry(id):
    entry = Entry.query.get_or_404(id)
    entry.status = not entry.status
    db.session.commit()
    flash('Entry marked as done.' if entry.status else 'Entry marked as not done.', 'success')
    return redirect(url_for('index'))

@app.route('/turn/<int:id>')
def turn(id):
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return render_template('errors/500.html'), 500