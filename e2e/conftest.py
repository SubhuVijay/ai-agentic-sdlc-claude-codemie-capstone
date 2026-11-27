import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


@pytest.fixture(scope='session')
def e2e_db_path():
    path = Path(tempfile.mkdtemp(prefix='entries-e2e-')) / 'e2e.db'
    assert path.resolve() != (ROOT / 'app' / 'app.db').resolve()
    return path


@pytest.fixture(scope='session')
def base_url(e2e_db_path):
    env = dict(os.environ, FLASK_APP='crudapp.py',
               DATABASE_URL='sqlite:///' + e2e_db_path.as_posix(),
               SECRET_KEY='e2e-secret')
    subprocess.run([sys.executable, '-m', 'flask', 'db', 'upgrade'], cwd=ROOT, env=env, check=True,
                   capture_output=True)
    port = _free_port()
    server = subprocess.Popen([sys.executable, '-m', 'flask', 'run', '--port', str(port)],
                              cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f'http://127.0.0.1:{port}'
    try:
        for _ in range(100):
            try:
                urllib.request.urlopen(url, timeout=1)
                break
            except OSError:
                if server.poll() is not None:
                    raise RuntimeError('flask server exited early')
                time.sleep(0.2)
        else:
            raise RuntimeError('flask server did not start')
        yield url
    finally:
        server.terminate()
        server.wait(timeout=10)


@pytest.fixture(autouse=True)
def clean_db(base_url, e2e_db_path):
    conn = sqlite3.connect(e2e_db_path)
    conn.execute('DELETE FROM entries')
    conn.commit()
    conn.close()
