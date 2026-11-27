# Flask CRUD App

A small Python Flask app for creating, listing, editing, and deleting entries. Data is stored in SQLite through Flask-SQLAlchemy, and schema changes are applied with Flask-Migrate.

Each entry has a title, a description, and a done/not-done status.

## Tech stack

| Layer | Technology |
|-------|------------|
| Language | Python 3 |
| Web framework | Flask 2.1 |
| Templates | Jinja2 |
| UI | Bootstrap 4.1 (CDN) |
| ORM | Flask-SQLAlchemy 2.5, SQLAlchemy 1.4 |
| Database | SQLite (`app/app.db`, or `DATABASE_URL`) |
| Migrations | Flask-Migrate 3.1 (Alembic) |

Pinned versions are in `requirements.txt`. Keep them as listed. Newer SQLAlchemy releases are not compatible with this app as written.

## Requirements

- Python 3
- The packages in `requirements.txt`

## Setup

```bash
git clone https://github.com/SubhuVijay/ai-agentic-sdlc-claude-codemie-capstone.git
cd ai-agentic-sdlc-claude-codemie-capstone
python -m venv venv
```

Activate the virtual environment, then install dependencies, create the database and start the app. The `migrations/` folder is committed, so there is no `flask db init` step.

**Linux / macOS**

```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
export FLASK_APP=crudapp.py
flask db upgrade
flask run
```

**Windows (PowerShell)**

```powershell
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
$env:FLASK_APP="crudapp.py"
flask db upgrade
flask run
```

`flask db upgrade` creates `app/app.db` (not committed) with the `entries` table. Open http://127.0.0.1:5000.

Environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `DATABASE_URL` | SQLAlchemy database URI | `sqlite:///.../app/app.db` |
| `SECRET_KEY` | Signs sessions, flash messages and CSRF tokens | A development-only key. Always set this in production. |

### Changing the schema

After editing `app/models.py`, generate and apply a migration, and commit the new file in `migrations/versions/`:

```bash
flask db migrate -m "describe the change"
flask db upgrade
```

## Usage

The home page lists every entry, or shows an empty state with a link to create one. Title (max 64 characters) and description (max 120 characters) are required, and surrounding whitespace is trimmed. New entries start as not done.

| Action | How |
|--------|-----|
| Create | **Create entry**, fill in the form, then **Create** |
| Edit | **Edit** on a row, then **Update** |
| Toggle status | **Turn Status** on that row |
| Delete | **Delete** on a row, then confirm on the next page |

Successful actions show a flash message. Validation errors show next to the field and nothing is saved. Unknown entry ids show a 404 page. Every form is CSRF protected (Flask-WTF), and every change is made with POST.

## Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | List all entries |
| GET | `/index` | Redirects to `/` |
| GET | `/entries/new` | Create form |
| POST | `/entries` | Create an entry (`title`, `description`) |
| GET | `/entries/<id>/edit` | Edit form |
| POST | `/entries/<id>` | Save title and description |
| POST | `/entries/<id>/toggle` | Toggle the entry's status |
| GET | `/entries/<id>/delete` | Delete confirmation page |
| POST | `/entries/<id>/delete` | Delete the entry |

The old `/add`, `/update/<id>`, `/delete/<id>` and `/turn/<id>` URLs only redirect to the routes above. They never change data.

## Tests

Install the test dependencies:

```bash
pip install -r requirements-dev.txt
```

**Unit and integration tests (pytest).** These use a temporary SQLite database, never `app/app.db`.

```bash
pytest -q
```

**End-to-end tests (Playwright).** These start `flask run` on a free port against a temporary database built with `flask db upgrade`. Install the browser once:

```bash
playwright install chromium
pytest e2e -q
```

## Project layout

```
crudapp.py              # entry point for flask run and flask db
app/__init__.py         # Flask app, SQLAlchemy, Flask-Migrate and CSRF protection
app/config.py           # Config (database URI, secret key)
app/models.py           # Entry model
app/routes.py           # HTTP routes and error handlers
app/templates/          # Jinja2 templates (extend base.html)
app/templates/errors/   # 404 and 500 pages
migrations/             # Alembic migrations
tests/                  # pytest tests
e2e/                    # Playwright tests
requirements.txt
requirements-dev.txt
```

### Entry

| Column | Type | Notes |
|--------|------|-------|
| `id` | integer | Primary key |
| `title` | string | Max 64 characters |
| `description` | string | Max 120 characters |
| `status` | boolean | Defaults to `False` (not done) |

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
