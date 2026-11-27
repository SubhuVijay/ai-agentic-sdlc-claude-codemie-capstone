# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project overview

A small Python Flask CRUD app backed by SQLite (via Flask-SQLAlchemy and Flask-Migrate). It manages a single model, `Entry`, with a title, description, and a boolean status (done/not done).

## Layout

- `crudapp.py`: entry point. Imports `app` from the `app` package so `flask run` and `flask db` commands can find it.
- `app/__init__.py`: creates the Flask app, `db` (SQLAlchemy), and `migrate` (Flask-Migrate). Imports `routes` and `models` at the bottom.
- `app/config.py`: `Config` class. Database URI comes from `DATABASE_URL` if set, otherwise `app/app.db`.
- `app/models.py`: `Entry` model (`id`, `title` ≤64 chars, `description` ≤120 chars, `status` bool).
- `app/routes.py`: all HTTP routes (index, add, update, delete, toggle status).
- `app/templates/`: Jinja2 templates (`base.html`, `header.html`, `footer.html`, `content.html`, `index.html`, `update.html`).
- `requirements.txt`: pinned dependencies. Do not upgrade pinned versions without checking compatibility with Python and SQLAlchemy 1.4.x.

## Setup and run

The README targets Linux. On Windows (PowerShell), use `venv\Scripts\activate` instead of `source venv/bin/activate`.

```
python -m venv venv
pip install --upgrade pip
pip install -r requirements.txt
set FLASK_APP=crudapp.py        # PowerShell: $env:FLASK_APP="crudapp.py"
flask db init                   # only once; creates the migrations/ folder
flask db migrate -m "entries table"
flask db upgrade
flask run
```

`app.db` and `migrations/` are not committed. Create them locally with the commands above.

## Routes

| Method | Path               | Purpose                          |
|--------|--------------------|----------------------------------|
| GET    | `/`, `/index`      | List all entries                 |
| POST   | `/add`             | Create an entry (form: title, description) |
| GET    | `/update/<id>`     | Show edit form for an entry      |
| POST   | `/update/<id>`     | Save edits to an entry           |
| GET    | `/delete/<id>`     | Delete an entry                  |
| GET    | `/turn/<id>`       | Toggle an entry's status         |

## Conventions

- Use Flask-SQLAlchemy sessions: `db.session.add/delete` then `db.session.commit()`.
- Schema changes go through Flask-Migrate (`flask db migrate` then `flask db upgrade`). Do not edit the database by hand.
- Keep templates in `app/templates/` and extend `base.html`.
- Match the existing style: plain Flask functions, no blueprints or service layer.

## Known issues

These exist in the current code. Check them before assuming behavior is intentional.

- `/add` in `app/routes.py` has an inverted condition: `if not title or description:` only saves when the title is empty or the description is provided. It should probably be `if title and description:`. Invalid submissions currently fall through to a plain `"of the jedi"` response.
- Several routes use `if not id or id != 0:`, which is effectively always true for valid IDs. It has no real effect but is confusing.
- Error responses return the literal string `"of the jedi"` instead of a proper 404 or redirect.
- `SECRET_KEY` is hardcoded in `app/config.py`. The environment-variable version is commented out. Do not use this key in production.
- Field length limits (`title` 64, `description` 120) are not checked by the form or routes. SQLite also does not enforce `VARCHAR` lengths, so long input is stored without error.

## Working in this repo

- Before changing behavior, read the relevant route, model, and template together.
- Run the app with `flask run` and test the affected route in the browser or with `curl` after changes.
- Do not commit `app.db`, `venv/`, or `migrations/` unless the user asks.
