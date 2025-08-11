import json
from typing import Optional, Dict, Any
from urllib.parse import urljoin

from httpx import Client, HTTPError, TimeoutException
from loguru import logger


class Request:
    def __init__(
        self, endpoint: str, base_url: str = None, headers: Dict[str, str] = None
    ):
        self.base_url = base_url or "https://api.mzmc.top"
        self.endpoint = endpoint
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (compatible; MzmcOS; +https://mzmc.top) MzmcOS/Loader",
            "Content-Type": "application/json",
        }
        self.client = Client(timeout=10)  # 默认10秒超时

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def _build_url(self) -> str:
        """构建完整请求URL"""
        return urljoin(self.base_url, self.endpoint)

    @staticmethod
    def _handle_response(response) -> Any:
        """统一处理响应"""
        try:
            response.raise_for_status()
            result = response.json()
            logger.trace(f"API Response: {result}")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"HTTP错误: {e} - 原始响应: {response.text}")
            raise ValueError(f"JSON解析失败: {e} - 原始响应: {response.text}")
        except HTTPError as e:
            logger.error(f"HTTP错误: {e} - 原始响应: {response.text}")
            raise RuntimeError(f"HTTP错误 {response.status_code}: {e}")

    def _send_request(self, method: str, **kwargs) -> Any:
        """通用请求方法"""
        url = self._build_url()
        try:
            response = self.client.request(method=method, url=url, **kwargs)
            return self._handle_response(response)
        except TimeoutException as e:
            raise RuntimeError(f"请求超时: {e}")
        except Exception as e:
            raise RuntimeError(f"请求异常: {e}")


class Get(Request):
    def get(
        self,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        header: Optional[Dict] = None,
    ) -> Any:
        """GET请求
        :param data: 表单数据
        :param json_data: JSON数据
        :param params: 查询参数
        :param header: 请求头
        """
        return self._send_request(
            "GET", data=data, json=json_data, params=params, headers=header
        )


class Post(Request):
    def post(
        self,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        header: Optional[Dict] = None,
    ) -> Any:
        """POST请求
        :param data: 表单数据
        :param json_data: JSON数据
        :param params: 查询参数
        :param header: 头
        """
        return self._send_request(
            "POST", data=data, json=json_data, params=params, headers=header
        )


class Patch(Request):
    def patch(
        self,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        header: Optional[Dict] = None,
    ) -> Any:
        """POST请求
        :param data: 表单数据
        :param json_data: JSON数据
        :param params: 查询参数
        :param header: 头
        """
        return self._send_request(
            "PATCH", data=data, json=json_data, params=params, headers=header
        )


class Delete(Request):
    def delete(
        self,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        header: Optional[Dict] = None,
    ) -> Any:
        """POST请求
        :param data: 表单数据
        :param json_data: JSON数据
        :param params: 查询参数
        :param header: 头
        """
        return self._send_request(
            "DELETE", data=data, json=json_data, params=params, headers=header
        )
