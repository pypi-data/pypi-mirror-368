from lsrestclient.mock import lsrestclient_mock_context

try:
    import pytest

    @pytest.fixture
    def lsrestclient_mocker():
        with lsrestclient_mock_context() as mocker:
            yield mocker

except ImportError:
    pass
