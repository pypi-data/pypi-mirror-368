from .request import Post, Get, Delete, Patch


class Info:
    def __init__(self):
        pass

    @staticmethod
    def _request(endpoint: str) -> dict:
        with Get(endpoint=endpoint) as api:
            return api.get()

    def server_status(self) -> list:
        return self._request("/info/status")

    def online_players(self) -> dict:
        return self._request("/info/status/online_players")

    def get_version(self, product_id: str) -> dict:
        return self._request(f"/info/version/{product_id}")


class Version:
    def __init__(self):
        super().__init__()

    @staticmethod
    def _get(endpoint: str, access_token: str = None, payloads: dict = None) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
        with Get(endpoint=endpoint) as api:
            return api.get(json_data=payloads, header=headers)

    @staticmethod
    def _post(endpoint: str, payloads: dict = None, access_token: str = None) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
        with Post(endpoint=endpoint) as api:
            return api.post(json_data=payloads, header=headers)

    @staticmethod
    def _delete(endpoint: str, payloads: dict = None, access_token: str = None) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
        with Delete(endpoint=endpoint) as api:
            return api.delete(json_data=payloads, header=headers)

    @staticmethod
    def _patch(endpoint: str, payloads: dict = None, access_token: str = None) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
        with Patch(endpoint=endpoint) as api:
            return api.patch(json_data=payloads, header=headers)

    def get_version(self, client_id: str) -> dict:
        return self._get(endpoint=f"/info/version/{client_id}")

    def add_client(self, client_name: str, description: str, access_token: str):
        return self._post(
            endpoint="/info/version",
            payloads={"client_name": client_name, "description": description},
            access_token=access_token,
        )

    def delete_client(self, client_id: str, access_token: str):
        return self._delete(
            endpoint=f"/info/version/{client_id}", access_token=access_token
        )

    def update_client(
        self, client_id: str, client_name: str, description: str, access_token: str
    ):
        return self._patch(
            endpoint=f"/info/version/{client_id}",
            payloads={
                "id": client_id,
                "client_name": client_name,
                "description": description,
            },
            access_token=access_token,
        )

    def set_version(self, client_id: str, x: int, y: int, z: int, access_token: str):
        return self._post(
            endpoint=f"/info/version/set/{client_id}",
            payloads={"x": x, "y": y, "z": z},
            access_token=access_token,
        )

    def increase_version(self, client_id: str, part: str, access_token: str):
        return self._post(
            endpoint=f"/info/version/increase/{client_id}",
            payloads={"part": part},
            access_token=access_token,
        )


if __name__ == "__main__":
    # 建议添加异常处理
    try:
        info = Info()
        print("服务器状态:", info.server_status())
        print("在线玩家:", info.online_players())
    except RuntimeError as e:
        print(f"API请求失败: {str(e)}")
    except ValueError as e:
        print(f"响应解析错误: {str(e)}")
