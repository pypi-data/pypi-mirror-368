import pathlib
import uuid
from unittest.mock import patch

import pytest
from click.testing import CliRunner


def _get_repo_root_dir() -> str:
    """
    :return: path to the project folder.
    `tests/` should be in the same folder and this file should be in the root of `tests/`.
    """
    return str(pathlib.Path(__file__).parent.parent)


fixed_now = "2024-03-29T09:49:23.836557+01:00"
fixed_uuid = uuid.UUID("12345678-1234-5678-1234-567812345678")

ROOT_DIR = _get_repo_root_dir()
RESOURCES = pathlib.Path(f"{ROOT_DIR}/tests/resources")


@pytest.fixture(scope="session")
def freeze():
    with patch("bitwarden_import_msecure.bitwarden_json.now_string", return_value=fixed_now):
        yield


@pytest.fixture
def runner(freeze):
    return CliRunner(echo_stdin=True)


@pytest.fixture
def msecure_export():
    with open(RESOURCES / "mSecure Export File.csv") as f:
        yield f.read()


@pytest.fixture
def bitwarden_file():
    return RESOURCES / "bitwarden_export.json"


@pytest.fixture
def bitwarden_patched_file():
    return RESOURCES / "bitwarden_patched_export.json"


@pytest.fixture
def bitwarden_broken_file():
    return RESOURCES / "bitwarden_broken_export.json"


@pytest.fixture
def bitwarden_notes_file():
    return RESOURCES / "bitwarden_notes_export.json"


@pytest.fixture
def bitwarden_csv_file():
    return RESOURCES / "bitwarden_export.csv"


@pytest.fixture
def bitwarden_notes_csv_file():
    return RESOURCES / "bitwarden_notes_export.csv"
