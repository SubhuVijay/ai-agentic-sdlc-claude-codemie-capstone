# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project overview

A small Python Flask CRUD app backed by SQLite (via Flask-SQLAlchemy and Flask-Migrate). It manages a single model, `Entry`, with a title, description, and a boolean status (done/not done).

## Layout

- `crudapp.py`: entry point. Imports `app` from the `app` package so `flask run` and `flask db` commands can find it.
- `app/__init__.py`: creates the Flask app, `db` (SQLAlchemy), `migrate` (Flask-Migrate), and `csrf` (Flask-WTF `CSRFProtect`). Imports `routes` and `models` at the bottom.
- `app/config.py`: `Config` class. Database URI comes from `DATABASE_URL` if set, otherwise `app/app.db`. `SECRET_KEY` comes from the environment, with a development-only fallback.
- `app/models.py`: `Entry` model on table `entries` (`id`, `title` ≤64 chars, `description` ≤120 chars, `status` bool, not null, default false).
- `app/routes.py`: all HTTP routes, shared form validation (`read_entry_form`), and the 404/500 error handlers.
- `app/templates/`: Jinja2 templates (`base.html`, `header.html`, `footer.html`, `index.html`, `entry_form.html`, `entry_delete_confirm.html`, `errors/404.html`, `errors/500.html`).
- `migrations/`: Alembic migrations (committed).
- `tests/`: pytest tests using a temporary SQLite DB. `e2e/`: Playwright tests that start `flask run` against a temporary DB.
- `requirements.txt`: pinned dependencies. Do not upgrade pinned versions without checking compatibility with Python and SQLAlchemy 1.4.x.

## Setup and run

The README targets Linux. On Windows (PowerShell), use `venv\Scripts\activate` instead of `source venv/bin/activate`.

```
python -m venv venv
pip install --upgrade pip
pip install -r requirements.txt
set FLASK_APP=crudapp.py        # PowerShell: $env:FLASK_APP="crudapp.py"
flask db upgrade                # creates app/app.db from the committed migrations
flask run
```

`app.db` is not committed. `migrations/` is committed.

## Tests

```
pip install -r requirements-dev.txt
pytest -q                       # unit/integration, isolated temp DB
playwright install chromium     # first time only
pytest e2e -q                   # browser tests, isolated temp DB
```

## Routes

| Method | Path                      | Purpose                          |
|--------|---------------------------|----------------------------------|
| GET    | `/`                       | List all entries                 |
| GET    | `/index`                  | Redirect to `/`                  |
| GET    | `/entries/new`            | Create form                      |
| POST   | `/entries`                | Create an entry (form: title, description) |
| GET    | `/entries/<id>/edit`      | Edit form                        |
| POST   | `/entries/<id>`           | Save edits                       |
| POST   | `/entries/<id>/toggle`    | Toggle status                    |
| GET    | `/entries/<id>/delete`    | Delete confirmation page         |
| POST   | `/entries/<id>/delete`    | Delete the entry                 |

Legacy `/add`, `/update/<id>`, `/delete/<id>` and `/turn/<id>` only redirect to the routes above and never change data. All changes are POST and CSRF protected, so every form needs `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`. Missing ids return the custom 404 page.

## Conventions

- Use Flask-SQLAlchemy sessions: `db.session.add/delete` then `db.session.commit()`.
- Schema changes go through Flask-Migrate (`flask db migrate` then `flask db upgrade`). Do not edit the database by hand. Commit new files in `migrations/versions/`.
- Validate title/description with `read_entry_form` (trim, required, max 64/120). Validation failures return 200 with inline errors and do not commit.
- Keep templates in `app/templates/` and extend `base.html`.
- Match the existing style: plain Flask functions, no blueprints or service layer.

## Known issues

- `SECRET_KEY` falls back to a hardcoded development key when the `SECRET_KEY` environment variable is unset. Always set it in production.
- SQLite does not enforce `VARCHAR` lengths, so the 64/120 limits are enforced only by `read_entry_form` in `app/routes.py`.
- Legacy POST redirects (`/add`, `/update/<id>`) use 307. Werkzeug's test client drops the form body when following them, so test them without `follow_redirects`.

## Working in this repo

- Before changing behavior, read the relevant route, model, and template together.
- Run `pytest -q` (and `pytest e2e -q` for UI changes) after changes. Tests must never touch `app/app.db`.
- Do not commit `app.db` or `venv/`.
