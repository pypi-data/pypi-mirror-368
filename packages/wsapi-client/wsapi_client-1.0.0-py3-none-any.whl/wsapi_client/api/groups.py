from __future__ import annotations
from ..http import WSApiHttp, ApiResponse
from ..models.entities.groups.group_info import GroupInfo


class GroupsClient:
    def __init__(self, http: WSApiHttp) -> None:
        self._http = http

    def list(self) -> list[GroupInfo]:
        return self._http.send_json("GET", "/groups", model=list[GroupInfo])

    def get(self, group_id: str) -> GroupInfo:
        return self._http.send_json("GET", f"/groups/{group_id}", model=GroupInfo)

    def update_description(self, group_id: str, payload: dict) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/description", model=dict, json=payload)

    def update_name(self, group_id: str, payload: dict) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/name", model=dict, json=payload)

    def leave(self, group_id: str) -> None:
        self._http.send_json("PUT", f"/groups/{group_id}/leave", model=dict)

    # Try variants
    def try_list(self) -> ApiResponse[list[GroupInfo]]:
        return self._http.try_send_json("GET", "/groups", model=list[GroupInfo])

    def try_get(self, group_id: str) -> ApiResponse[GroupInfo]:
        return self._http.try_send_json("GET", f"/groups/{group_id}", model=GroupInfo)

    def try_update_description(self, group_id: str, payload: dict) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/description", model=dict, json=payload)

    def try_update_name(self, group_id: str, payload: dict) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/name", model=dict, json=payload)

    def try_leave(self, group_id: str) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"/groups/{group_id}/leave", model=dict)
