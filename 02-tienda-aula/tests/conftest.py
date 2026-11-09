"""Servidor HTTP real en localhost y SQLite temporal para cada test E2E."""
import threading
import pytest
from werkzeug.serving import make_server
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app

@pytest.fixture
def servidor(tmp_path):
    app = create_app(tmp_path / "prueba_e2e.db")
    app.config["TESTING"] = True
    servidor_http = make_server("127.0.0.1", 0, app, threaded=True)
    hilo = threading.Thread(target=servidor_http.serve_forever, daemon=True)
    hilo.start()
    try:
        yield f"http://127.0.0.1:{servidor_http.server_port}", tmp_path / "prueba_e2e.db"
    finally:
        servidor_http.shutdown()
        hilo.join(timeout=5)
