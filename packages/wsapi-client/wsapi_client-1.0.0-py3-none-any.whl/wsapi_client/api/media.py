from __future__ import annotations

from ..http import WSApiHttp, ApiResponse
from ..models.requests.media.media_download_request import MediaDownloadRequest


class MediaClient:
    def __init__(self, http: WSApiHttp) -> None:
        self._http = http

    def download(self, req: MediaDownloadRequest) -> bytes:
        return self._http.send_bytes("POST", "/media/download", json=req.model_dump(by_alias=True))

    def try_download(self, req: MediaDownloadRequest) -> ApiResponse[bytes]:
        return self._http.try_send_bytes("POST", "/media/download", json=req.model_dump(by_alias=True))
