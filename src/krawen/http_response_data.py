from dataclasses import dataclass

from krawen.async_chunked_reader import AsyncChunkedReader


@dataclass
class HTTPResponseInfo:
    http_version: str
    status_code: int
    reason: str
    headers: dict[str, bytes]

    def get_header(self, key: str) -> bytes:
        return self.headers[key.lower()]

@dataclass
class HTTPResponseData:
    info: HTTPResponseInfo
    body: AsyncChunkedReader

    def __post_init__(self):
        self.headers = {key.lower(): value for key, value in self.info.headers.items()}
