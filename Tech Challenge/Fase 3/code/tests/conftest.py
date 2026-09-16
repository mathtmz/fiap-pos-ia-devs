from pathlib import Path
import sys
from uuid import uuid4

import pytest

CODE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_ROOT))
sys.path.insert(0, str(CODE_ROOT / "src"))


@pytest.fixture
def workspace_file(request):
    """Give filesystem tests a unique file path inside the writable project."""
    path = Path(__file__).resolve().parents[1] / "outputs" / f".test-{uuid4().hex}"
    request.addfinalizer(lambda: path.unlink(missing_ok=True))
    return path
