import os
import tempfile

_db_file = tempfile.NamedTemporaryFile(prefix="medflow-tests-", suffix=".db", delete=False)
_db_file.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_db_file.name}"
os.environ["SECRET_KEY"] = "test-only-secret-key-that-is-long-enough-32chars"
os.environ["APP_ENV"] = "test"
os.environ["DEMO_SEED"] = "false"

from app.database import Base, engine
from app import models

Base.metadata.create_all(bind=engine)

from app.main import app
from fastapi.testclient import TestClient
import pytest

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
