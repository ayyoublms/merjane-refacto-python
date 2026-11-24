# Getting started

Run these commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py test
python manage.py runserver
```

On Windows, create and activate the virtual environment using the commands in the root README. The development server runs at `http://127.0.0.1:8000/`.

## Database

The project uses SQLite. Running migrations creates `db.sqlite3` in the repository root. Connect to that file with a SQLite-compatible database client such as DBeaver. Django's built-in `auth_user` table appears after migrations have been applied.

## Order endpoint

The order-processing endpoint accepts POST requests at `/orders/<order_id>/processOrder`.

The supplied code does not register Order or Product in Django admin, so they are not available there by default.
