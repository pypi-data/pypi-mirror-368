from __future__ import annotations
from ..http import WSApiHttp, ApiResponse
from ..models.entities.contacts.contact_info import ContactInfo
from ..models.entities.contacts.contact_picture import ContactPicture
from ..models.entities.contacts.contact_business_profile import ContactBusinessProfile


class ContactsClient:
    def __init__(self, http: WSApiHttp) -> None:
        self._http = http

    # Standard methods
    def list(self) -> list[ContactInfo]:
        return self._http.send_json("GET", "/contacts", model=list[ContactInfo])

    def get(self, contact_id: str) -> ContactInfo:
        return self._http.send_json("GET", f"/contacts/{contact_id}", model=ContactInfo)

    def get_picture(self, contact_id: str) -> ContactPicture:
        return self._http.send_json("GET", f"/contacts/{contact_id}/picture", model=ContactPicture)

    def get_business_profile(self, contact_id: str) -> ContactBusinessProfile:
        return self._http.send_json("GET", f"/contacts/{contact_id}/business", model=ContactBusinessProfile)

    def create(self, payload: dict) -> None:
        self._http.send_json("POST", "/contacts", model=dict, json=payload)

    def update(self, contact_id: str, payload: dict) -> None:
        self._http.send_json("PUT", f"/contacts/{contact_id}", model=dict, json=payload)

    def subscribe_presence(self, contact_id: str) -> None:
        self._http.send_json("POST", f"/contacts/{contact_id}/presence", model=dict, json={})

    # Try methods
    def try_list(self) -> ApiResponse[list[ContactInfo]]:
        return self._http.try_send_json("GET", "/contacts", model=list[ContactInfo])

    def try_get(self, contact_id: str) -> ApiResponse[ContactInfo]:
        return self._http.try_send_json("GET", f"/contacts/{contact_id}", model=ContactInfo)

    def try_get_picture(self, contact_id: str) -> ApiResponse[ContactPicture]:
        return self._http.try_send_json("GET", f"/contacts/{contact_id}/picture", model=ContactPicture)

    def try_get_business_profile(self, contact_id: str) -> ApiResponse[ContactBusinessProfile]:
        return self._http.try_send_json("GET", f"/contacts/{contact_id}/business", model=ContactBusinessProfile)

    def try_create(self, payload: dict) -> ApiResponse[object]:
        return self._http.try_send_json("POST", "/contacts", model=dict, json=payload)

    def try_update(self, contact_id: str, payload: dict) -> ApiResponse[object]:
        return self._http.try_send_json("PUT", f"/contacts/{contact_id}", model=dict, json=payload)

    def try_subscribe_presence(self, contact_id: str) -> ApiResponse[object]:
        return self._http.try_send_json("POST", f"/contacts/{contact_id}/presence", model=dict, json={})
