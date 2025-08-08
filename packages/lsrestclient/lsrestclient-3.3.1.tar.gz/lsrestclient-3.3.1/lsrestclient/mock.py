import dataclasses
from contextlib import contextmanager
from typing import Union
from unittest.mock import MagicMock

from lsrestclient import LsRestClient


@dataclasses.dataclass
class LsRestClientMockModel:
    mock_name: str
    client: LsRestClient
    mock: MagicMock


class LsRestClientMocker(object):
    def __init__(self):
        super().__init__()
        self.mocks = {}

    def mock(self, client: Union[LsRestClient, str], method: str, url: str, *args, **kwargs):
        if isinstance(client, str):
            client = LsRestClient.client(client)

        mock_name = LsRestClient.mock_name(client.name, method, url)
        mock = MagicMock(*args, **kwargs)
        client.mock(mock_name, mock)
        self.mocks[mock_name] = LsRestClientMockModel(client=client, mock_name=mock_name, mock=mock)
        return mock

    def unmock_all(self):
        for mock_name, mock_model in self.mocks.items():
            mock_model.client.unmock(mock_name)
        self.mocks = {}

    def unmock(self, client: LsRestClient, method: str, url: str):
        mock_name = LsRestClient.mock_name(client.name, method, url)
        mock_model = self.mocks[mock_name]
        mock_model.client.unmock(mock_name)
        del self.mocks[mock_name]


@contextmanager
def lsrestclient_mock_context():
    mocker = LsRestClientMocker()
    yield mocker
    mocker.unmock_all()
