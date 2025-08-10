from __future__ import annotations
from ..http import WSApiHttp, ApiResponse
from ..models.entities.chats.chat_info import ChatInfo


class ChatsClient:
    def __init__(self, http: WSApiHttp) -> None:
        self._http = http

    def list(self) -> list[ChatInfo]:
        return self._http.send_json("GET", "/chats", model=list[ChatInfo])

    def get(self, chat_id: str) -> ChatInfo:
        return self._http.send_json("GET", f"/chats/{chat_id}", model=ChatInfo)

    # Try
    def try_list(self) -> ApiResponse[list[ChatInfo]]:
        return self._http.try_send_json("GET", "/chats", model=list[ChatInfo])

    def try_get(self, chat_id: str) -> ApiResponse[ChatInfo]:
        return self._http.try_send_json("GET", f"/chats/{chat_id}", model=ChatInfo)
