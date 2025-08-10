from importlib.metadata import PackageNotFoundError
from unittest.mock import Mock

from .find_version import find_version


def test_from_metadata(monkeypatch):
    mock_version = Mock(return_value='1.2.3')
    monkeypatch.setattr('importlib.metadata.version', mock_version)

    result = find_version()

    assert result == '1.2.3'
    assert mock_version.call_args[0] == ('ndice',)


def test_from_pyproject(monkeypatch):
    mock_version = Mock(side_effect=PackageNotFoundError)
    monkeypatch.setattr('importlib.metadata.version', mock_version)

    fake_pyproject = {
        'project': {
            'version': '2.3.4',
        }
    }
    mock_loads = Mock(return_value=fake_pyproject)
    monkeypatch.setattr('tomllib.loads', mock_loads)

    result = find_version()

    assert result == '2.3.4'


def test_default_version(monkeypatch):
    mock_version = Mock(side_effect=PackageNotFoundError)
    monkeypatch.setattr('importlib.metadata.version', mock_version)

    mock_loads = Mock(side_effect=RuntimeError)
    monkeypatch.setattr('tomllib.loads', mock_loads)

    result = find_version()

    assert result == '0.0.0+unknown'
