try:
    from .request import Post, Get, Delete
except Exception:
    from request import Post, Get, Delete


class Player:
    def __init__(self):
        super().__init__()

    @staticmethod
    def _get(endpoint: str, access_token: str = None, payloads: dict = None) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
        with Get(endpoint=endpoint) as api:
            return api.get(json_data=payloads, header=headers)

    @staticmethod
    def _post(endpoint: str, payloads: dict, access_token: str = None) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
        with Post(endpoint=endpoint) as api:
            return api.post(json_data=payloads, header=headers)

    @staticmethod
    def _delete(endpoint: str, payloads: dict, access_token: str = None) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
        with Delete(endpoint=endpoint) as api:
            return api.delete(json_data=payloads, header=headers)

    def profile(self, access_token: str = None) -> dict:
        return self._get("/player/profile", access_token)

    def profile_by_id(self, uid: int, access_token: str = None) -> dict:
        return self._get(f"/player/profile/id/{uid}", access_token)

    def profile_by_username(self, username: str, access_token: str = None) -> dict:
        return self._get(f"/player/profile/username/{username}", access_token)

    def profile_of_all(self, access_token: str = None) -> dict:
        return self._get("/player/profile/all", access_token)

    def add_whitelist(self, realname: str, access_token: str = None):
        payload = {"realname": realname}
        return self._post("/player/whitelist", payload, access_token)

    def get_whitelist(self, keyword: str, access_token: str = None):
        payload = {"keyword": keyword}
        return self._get("/player/whitelist", access_token, payload)

    def delete_whitelist(self, uid: int, access_token: str = None):
        payload = {"id": uid}
        return self._delete(f"/player/whitelist/{uid}", payload, access_token)
