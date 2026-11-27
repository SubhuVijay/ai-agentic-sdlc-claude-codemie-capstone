from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Entry

jedi = "of the jedi"

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

@app.route('/update/<int:id>')
def updateRoute(id):
    if not id or id != 0:
        entry = Entry.query.get(id)
        if entry:
            return render_template('update.html', entry=entry)

    return "of the jedi"

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    if not id or id != 0:
        entry = Entry.query.get(id)
        if entry:
            form = request.form
            title = form.get('title')
            description = form.get('description')
            entry.title = title
            entry.description = description
            db.session.commit()
        return redirect('/')

    return "of the jedi"



@app.route('/delete/<int:id>')
def delete(id):
    if not id or id != 0:
        entry = Entry.query.get(id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
        return redirect('/')

    return "of the jedi"

@app.route('/turn/<int:id>')
def turn(id):
    if not id or id != 0:
        entry = Entry.query.get(id)
        if entry:
            entry.status = not entry.status
            db.session.commit()
        return redirect('/')

    return "of the jedi"

# @app.errorhandler(Exception)
# def error_page(e):
#     return "of the jedi"