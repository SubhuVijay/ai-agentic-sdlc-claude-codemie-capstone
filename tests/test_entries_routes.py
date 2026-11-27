import pytest


# ---- list and /index alias -------------------------------------------------

def test_list_empty_state(client):
    resp = client.get('/')
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert 'id="empty-state"' in html
    assert '/entries/new' in html


def test_list_shows_entries_in_id_order(client, make_entry):
    make_entry(title='First', status=False)
    make_entry(title='Second', status=True)
    html = client.get('/').get_data(as_text=True)
    assert 'id="empty-state"' not in html
    assert html.index('First') < html.index('Second')
    assert 'Not done' in html and 'Done' in html


def test_index_alias_redirects_to_root(client):
    resp = client.get('/index')
    assert resp.status_code in (301, 302)
    assert resp.headers['Location'].endswith('/')
    assert client.get('/index', follow_redirects=True).request.path == '/'


# ---- create ----------------------------------------------------------------

def test_new_form_has_csrf_token(client):
    resp = client.get('/entries/new')
    assert resp.status_code == 200
    assert 'name="csrf_token"' in resp.get_data(as_text=True)


def test_create_valid_entry(client, csrf, get_entry, entry_count):
    resp = client.post('/entries', data={'title': '  Hello ', 'description': ' World  ',
                                         'csrf_token': csrf()})
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/')
    assert entry_count() == 1
    assert get_entry(1) == ('Hello', 'World', False)
    assert 'Entry created.' in client.get('/').get_data(as_text=True)


@pytest.mark.parametrize('title,description,expected', [
    ('', 'desc', ['Title is required.']),
    ('   ', 'desc', ['Title is required.']),
    ('t', '', ['Description is required.']),
    ('t', '   ', ['Description is required.']),
    ('x' * 65, 'desc', ['Title must be 64 characters or fewer.']),
    ('t', 'y' * 121, ['Description must be 120 characters or fewer.']),
    ('', '', ['Title is required.', 'Description is required.']),
])
def test_create_validation_errors(client, csrf, entry_count, title, description, expected):
    resp = client.post('/entries', data={'title': title, 'description': description,
                                         'csrf_token': csrf()})
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    for message in expected:
        assert message in html
    assert entry_count() == 0


def test_create_accepts_max_lengths(client, csrf, entry_count):
    resp = client.post('/entries', data={'title': 'x' * 64, 'description': 'y' * 120,
                                         'csrf_token': csrf()})
    assert resp.status_code == 302
    assert entry_count() == 1


def test_create_validation_error_keeps_input(client, csrf):
    resp = client.post('/entries', data={'title': '', 'description': 'keep me',
                                         'csrf_token': csrf()})
    assert 'keep me' in resp.get_data(as_text=True)


def test_create_escapes_html(client, csrf):
    client.post('/entries', data={'title': '<b>bold</b>', 'description': 'd', 'csrf_token': csrf()})
    html = client.get('/').get_data(as_text=True)
    assert '&lt;b&gt;bold&lt;/b&gt;' in html
    assert '<b>bold</b>' not in html


# ---- edit / update ---------------------------------------------------------

def test_edit_form_prefilled(client, make_entry):
    entry_id = make_entry(title='Old title', description='Old desc')
    resp = client.get(f'/entries/{entry_id}/edit')
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert 'value="Old title"' in html
    assert 'Old desc</textarea>' in html
    assert f'action="/entries/{entry_id}"' in html
    assert 'name="csrf_token"' in html


def test_update_valid_entry(client, csrf, make_entry, get_entry):
    entry_id = make_entry(title='Old', description='Old', status=True)
    resp = client.post(f'/entries/{entry_id}', data={
        'title': ' New ', 'description': ' New desc ', 'csrf_token': csrf(f'/entries/{entry_id}/edit')})
    assert resp.status_code == 302
    assert get_entry(entry_id) == ('New', 'New desc', True)
    assert 'Entry updated.' in client.get('/').get_data(as_text=True)


@pytest.mark.parametrize('title,description,message', [
    ('', 'd', 'Title is required.'),
    ('x' * 65, 'd', 'Title must be 64 characters or fewer.'),
    ('t', '   ', 'Description is required.'),
    ('t', 'y' * 121, 'Description must be 120 characters or fewer.'),
])
def test_update_validation_errors_do_not_commit(client, csrf, make_entry, get_entry,
                                                title, description, message):
    entry_id = make_entry(title='Old', description='Old desc')
    resp = client.post(f'/entries/{entry_id}', data={
        'title': title, 'description': description, 'csrf_token': csrf(f'/entries/{entry_id}/edit')})
    assert resp.status_code == 200
    assert message in resp.get_data(as_text=True)
    assert get_entry(entry_id) == ('Old', 'Old desc', False)


def test_edit_missing_id_is_404(client):
    resp = client.get('/entries/999/edit')
    assert resp.status_code == 404
    assert '<h1>404</h1>' in resp.get_data(as_text=True)


def test_update_missing_id_is_404(client, csrf):
    resp = client.post('/entries/999', data={'title': 'a', 'description': 'b', 'csrf_token': csrf()})
    assert resp.status_code == 404
    assert '<h1>404</h1>' in resp.get_data(as_text=True)


# ---- toggle ----------------------------------------------------------------

def test_toggle_flips_status_both_ways(client, csrf, make_entry, get_entry):
    entry_id = make_entry()
    resp = client.post(f'/entries/{entry_id}/toggle', data={'csrf_token': csrf('/')})
    assert resp.status_code == 302
    assert get_entry(entry_id)[2] is True
    assert 'Entry marked as done.' in client.get('/').get_data(as_text=True)

    client.post(f'/entries/{entry_id}/toggle', data={'csrf_token': csrf('/')})
    assert get_entry(entry_id)[2] is False
    assert 'Entry marked as not done.' in client.get('/').get_data(as_text=True)


def test_toggle_missing_id_is_404(client, csrf):
    resp = client.post('/entries/999/toggle', data={'csrf_token': csrf()})
    assert resp.status_code == 404
    assert '<h1>404</h1>' in resp.get_data(as_text=True)


def test_toggle_rejects_get(client, make_entry, get_entry):
    entry_id = make_entry()
    assert client.get(f'/entries/{entry_id}/toggle').status_code == 405
    assert get_entry(entry_id)[2] is False


# ---- delete ----------------------------------------------------------------

def test_delete_confirm_page_does_not_delete(client, make_entry, entry_count):
    entry_id = make_entry(title='Doomed')
    resp = client.get(f'/entries/{entry_id}/delete')
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert 'Doomed' in html
    assert f'action="/entries/{entry_id}/delete"' in html
    assert 'name="csrf_token"' in html
    assert entry_count() == 1


def test_delete_removes_entry(client, csrf, make_entry, get_entry):
    entry_id = make_entry(title='Doomed')
    keep_id = make_entry(title='Keep')
    resp = client.post(f'/entries/{entry_id}/delete',
                       data={'csrf_token': csrf(f'/entries/{entry_id}/delete')})
    assert resp.status_code == 302
    assert get_entry(entry_id) is None
    assert get_entry(keep_id) is not None
    assert 'Entry deleted.' in client.get('/').get_data(as_text=True)


def test_delete_missing_id_is_404_for_confirm_and_post(client, csrf):
    assert client.get('/entries/999/delete').status_code == 404
    resp = client.post('/entries/999/delete', data={'csrf_token': csrf()})
    assert resp.status_code == 404
    assert '<h1>404</h1>' in resp.get_data(as_text=True)


# ---- CSRF ------------------------------------------------------------------

@pytest.mark.parametrize('path', ['/entries', '/entries/1', '/entries/1/toggle', '/entries/1/delete'])
def test_post_without_csrf_token_is_rejected(client, make_entry, get_entry, entry_count, path):
    make_entry(title='Orig', description='Orig desc')
    resp = client.post(path, data={'title': 'x', 'description': 'y'})
    assert resp.status_code == 400
    assert entry_count() == 1
    assert get_entry(1) == ('Orig', 'Orig desc', False)


# ---- legacy routes only redirect -------------------------------------------

def test_legacy_get_routes_redirect_and_do_not_mutate(client, make_entry, get_entry):
    entry_id = make_entry()
    assert client.get(f'/update/{entry_id}').headers['Location'].endswith(f'/entries/{entry_id}/edit')
    assert client.get(f'/delete/{entry_id}').headers['Location'].endswith(f'/entries/{entry_id}/delete')
    assert client.get(f'/turn/{entry_id}').headers['Location'].endswith('/')
    assert get_entry(entry_id) == ('Title', 'Description', False)


def test_legacy_post_routes_redirect_with_307(client, csrf):
    token = csrf()
    assert client.post('/add', data={'csrf_token': token}).headers['Location'].endswith('/entries')
    assert client.post('/update/1', data={'csrf_token': token}).headers['Location'].endswith('/entries/1')


# ---- error handlers --------------------------------------------------------

def test_unknown_url_renders_custom_404(client):
    resp = client.get('/no/such/page')
    assert resp.status_code == 404
    assert '<h1>404</h1>' in resp.get_data(as_text=True)


def test_server_error_renders_500_and_rolls_back(app, client, csrf, entry_count, monkeypatch):
    from app import db
    token = csrf()
    rolled_back = []
    real_rollback = db.session.rollback

    def failing_commit():
        raise RuntimeError('boom')

    def spy_rollback():
        rolled_back.append(True)
        real_rollback()

    monkeypatch.setitem(app.config, 'TESTING', False)
    monkeypatch.setattr(db.session, 'commit', failing_commit)
    monkeypatch.setattr(db.session, 'rollback', spy_rollback)
    resp = client.post('/entries', data={'title': 't', 'description': 'd', 'csrf_token': token})
    assert resp.status_code == 500
    assert '<h1>500</h1>' in resp.get_data(as_text=True)
    assert rolled_back
    monkeypatch.undo()
    assert entry_count() == 0


# ---- isolation -------------------------------------------------------------

def test_tests_use_isolated_database(app):
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    assert 'entries-pytest-' in uri
    assert not uri.endswith('app/app.db')
