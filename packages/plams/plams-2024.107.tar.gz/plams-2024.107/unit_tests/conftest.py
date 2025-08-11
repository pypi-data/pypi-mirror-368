import pytest
from pathlib import Path


@pytest.fixture
def xyz_folder():
    p = Path(__file__).parent.absolute() / "xyz"
    assert p.exists()
    return p
