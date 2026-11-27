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

Activate the virtual environment, then install dependencies and create the database.

**Linux / macOS**

```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
export FLASK_APP=crudapp.py
flask db init
flask db migrate -m "entries table"
flask db upgrade
flask run
```

**Windows (PowerShell)**

```powershell
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
$env:FLASK_APP="crudapp.py"
flask db init
flask db migrate -m "entries table"
flask db upgrade
flask run
```

`flask db init` is only needed once. It creates the `migrations/` folder. The database file is `app/app.db`. Neither `app.db` nor `migrations/` is part of the repository; create them locally with the commands above.

Open http://127.0.0.1:5000.

To use a different database, set `DATABASE_URL` before starting the app. When it is unset, the app uses `sqlite:///.../app/app.db`.

## Usage

The home page lists every entry and includes a form to add one. Title and description are required. New entries start as not done.

| Action | How |
|--------|-----|
| Add | Submit the form on the home page |
| Toggle status | **Turn Status** on that row |
| Edit | **Edit**, then save the update form |
| Delete | **Delete** on that row |

## Routes

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/`, `/index` | List all entries |
| POST | `/add` | Create an entry (`title`, `description`) |
| GET | `/update/<id>` | Show the edit form |
| POST | `/update/<id>` | Save title and description |
| GET | `/delete/<id>` | Delete an entry |
| GET | `/turn/<id>` | Toggle the entry's status |

## Project layout

```
crudapp.py              # entry point for flask run and flask db
app/__init__.py         # Flask app, SQLAlchemy, and Flask-Migrate
app/config.py           # Config (database URI, secret key)
app/models.py           # Entry model
app/routes.py           # HTTP routes
app/templates/          # Jinja2 templates (extend base.html)
requirements.txt
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
