from abc import ABC, abstractmethod

from lsrestclient import LsRestClient
import logging

log = logging.getLogger(__name__)


class LsFastApiClientBase(ABC):
    _client = None
    client_name = None

    def __init__(self):
        pass

    @classmethod
    def client(cls) -> LsRestClient:
        # noinspection PyBroadException
        try:
            cls._client = LsRestClient.client(cls.client_name)
        except Exception as e:  # pragma: no cover
            # noinspection PyArgumentList
            cls._client = cls.register()
        return cls._client

    @classmethod
    def register(cls, base_url: str = None, **kwargs) -> LsRestClient:
        # noinspection PyArgumentList
        log.debug(f"Registering {cls.client_name} API client at {base_url}")
        cls._client = LsRestClient(name=cls.client_name, base_url=base_url or cls.base_url(), **kwargs)
        return cls._client

    @classmethod
    def health(cls):
        return cls.client().get("/healthz")

    @classmethod
    @abstractmethod
    def base_url(cls):
        raise NotImplementedError
