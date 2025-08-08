import datetime
from dataclasses import dataclass
from typing import Optional

import lsjsonclasses
import pydash
from requests import Response
from requests.structures import CaseInsensitiveDict
from requests_cache import CachedResponse


@dataclass
class LsRestClientResponse:
    """
    Represents a response from the LsRestClient.
    """

    status_code: int
    content: str
    headers: CaseInsensitiveDict
    created_at: datetime.datetime | None = None
    expires: datetime.datetime | None = None
    cache_key: str | None = None
    revalidated: bool | None = None
    from_cache: bool | None = False

    _json: Optional[dict] = None

    def json(self):
        if self._json is None and self.content != "":
            self._json = lsjsonclasses.LSoftJSONDecoder.loads(self.content)
        return self._json

    @classmethod
    def from_requests_response(cls, response: Response):
        """
        Create an instance of LsRestClientResponse from a requests Response object.

        :param response: The requests Response object.
        :type response: Response
        :return: An instance of LsRestClientResponse representing the response.
        :rtype: LsRestClientResponse
        """

        encoding = pydash.get(response, "encoding", None)
        headers = pydash.get(response, "headers", None)
        content_type = headers.get("Content-Type", None)
        if content_type == "application/pdf":
            content = response.content
        else:
            content = response.content.decode("utf8" if encoding is None else encoding)

        ret = cls(status_code=response.status_code, content=content, headers=response.headers)
        if isinstance(response, CachedResponse):
            ret.created_at = response.created_at
            ret.expires = response.expires
            ret.cache_key = response.cache_key
            ret.revalidated = response.revalidated
            ret.from_cache = response.from_cache
        return ret

    @classmethod
    def from_dict(cls, status_code: int = 200, data: dict = None, headers: CaseInsensitiveDict = None):
        """
        Converts a dictionary into an instance of the LsRestClientResponse class.

        :param status_code: The HTTP status code. Defaults to 200.
        :param data: The data dictionary. Defaults to None.
        :param headers: The headers dictionary. Defaults to None.
        :return: An instance of the LsRestClientResponse class.

        """
        if data is None:
            data = {}
        if headers is None:
            headers = {}

        content = lsjsonclasses.LSoftJSONEncoder.dumps(data)

        return cls(status_code=status_code, content=content, headers=headers)
