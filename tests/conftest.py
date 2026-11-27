import os
import re
import tempfile
from pathlib import Path

_tmpdir = tempfile.mkdtemp(prefix='entries-pytest-')
TEST_DB = Path(_tmpdir) / 'test.db'
os.environ['DATABASE_URL'] = 'sqlite:///' + TEST_DB.as_posix()

import pytest
from app import app as flask_app, db
from app.models import Entry

REAL_DB = (Path(__file__).resolve().parent.parent / 'app' / 'app.db').as_posix()
assert REAL_DB not in flask_app.config['SQLALCHEMY_DATABASE_URI'], 'tests must not use app/app.db'

CSRF_RE = re.compile(r'name="csrf_token" value="([^"]+)"')


@pytest.fixture
def app():
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
    yield flask_app
    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def csrf(client):
    def fetch(path='/entries/new'):
        html = client.get(path).get_data(as_text=True)
        return CSRF_RE.search(html).group(1)
    return fetch


@pytest.fixture
def make_entry(app):
    def make(title='Title', description='Description', status=False):
        with app.app_context():
            entry = Entry(title=title, description=description, status=status)
            db.session.add(entry)
            db.session.commit()
            return entry.id
    return make


@pytest.fixture
def get_entry(app):
    def get(entry_id):
        with app.app_context():
            entry = db.session.get(Entry, entry_id)
            return None if entry is None else (entry.title, entry.description, entry.status)
    return get


@pytest.fixture
def entry_count(app):
    def count():
        with app.app_context():
            return Entry.query.count()
    return count
