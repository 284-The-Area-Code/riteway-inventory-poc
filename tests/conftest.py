import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))


def db_configured():
    return bool(os.environ.get("DATABASE_PASSWORD"))


requires_db = pytest.mark.skipif(
    not db_configured(),
    reason="DATABASE_PASSWORD is not set",
)


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from main import app

    return TestClient(app)
