from dataclasses import dataclass

from krawen.async_chunked_reader import AsyncChunkedReader


@dataclass
class HTTPResponseInfo:
    http_version: str
    status_code: int
    reason: str
    headers: dict[str, bytes]

    def __post_init__(self):
        self.headers = {key.lower(): value for key, value in self.headers.items()}

    def get_header(self, key: str) -> bytes:
        return self.headers[key.lower()]
    @property
    def content_type(self) -> bytes | None:
        try:
            return self.get_header("content-type")
        except KeyError:
            return None

@dataclass
class HTTPResponseData:
    info: HTTPResponseInfo
    body: AsyncChunkedReader

