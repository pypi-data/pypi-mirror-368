import contextlib
import logging
from typing import Optional, List, Type

import pydash
from webexception.webexception import WebException

log = logging.getLogger(__name__)


# noinspection PyShadowingBuiltins
class ConnectionError(Exception):
    """Exception class for connection errors.

    Args:
            url (Optional[str]): The URL that the connection could not be established to.

    Attributes:
            url (Optional[str]): The URL that the connection could not be established to.

    Raises:
            ConnectionError: If a connection could not be established to the given URL.

    """

    url: str

    def __init__(self, url: Optional[str] = None) -> None:
        self.url = url
        super().__init__(f"Connection could not be established to '{url}'")


class DownStreamError(Exception):
    status_code: int
    url: str
    content: str

    def __init__(self, url: str, status_code: int, content: str) -> None:
        self.url = url
        self.status_code = status_code
        self.content = content
        super().__init__(f"Downstream error calling {self.url}. {self.status_code} {self.content}")


@contextlib.contextmanager
def raise_errors(r, exceptions: Optional[List[Type[Exception]]] = None):
    if exceptions is None:
        exceptions_by_class = {}
    else:
        exceptions_by_class = {e.__name__: e for e in exceptions}

    if r.status_code < 399:
        yield r
    else:
        try:
            json = r.json()
        except Exception as e:
            log.error(r.content)
            raise WebException(status_code=r.status_code, detail=r.content)

        detail = pydash.get(json, "detail", json)
        error_class = pydash.get(detail, "error_class", None)
        if error_class is not None:
            payload = pydash.get(detail, "error_payload", {})
        else:
            error_class = pydash.get(detail, "ERROR_CLASS", None)
            payload = {}

        if error_class in exceptions_by_class:
            e = exceptions_by_class[error_class](**payload)
            raise e
        # backend errors
        raise WebException(status_code=r.status_code, detail=detail)
