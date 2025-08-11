from typing import Dict, Any, List, Optional

try:
    from .request import Get
except Exception:
    from request import Get


class EaverseAPIClient:
    """
    EaverseAPI SDK 客户端

    提供对MzmcAPI的访问接口,支持资源链接获取功能和聚落信息查询
    """

    def __init__(self, base_url: str = "https://mzmc-api.eaverse.top"):
        """
        初始化客户端

        Args:
            base_url: API基础地址，默认使用官方地址
        """
        self.base_url = base_url
        self.headers = {"User-Agent": "MzmcAPISDK/1.0"}

    def get_launcher_link(self) -> Dict[str, Any]:
        """
        获取启动器下载链接
        """
        url = "/api/v2/link/launcher"
        with Get(base_url=self.base_url, endpoint=url) as api:
            return api.get(header=self.headers)
    
    def get_all_areas(self) -> Dict[str, Any]:
        """
        获取聚落列表
        
        获取已录入系统的绵中方块人服务器上所有聚落的详细信息
        
        Returns:
            Dict[str, Any]: 包含所有聚落信息的响应数据
        """
        url = "/api/v2/area/all"
        with Get(base_url=self.base_url, endpoint=url) as api:
            return api.get(header=self.headers)
    
    def search_area(self, name: str) -> Dict[str, Any]:
        """
        模糊查询聚落信息
        
        通过聚落名称关键词模糊查询绵中方块人服务器上的聚落信息
        
        Args:
            name: 聚落名称关键词
            
        Returns:
            Dict[str, Any]: 包含匹配聚落信息的响应数据
        """
        url = f"/api/v2/area/search/?name={name}"
        with Get(base_url=self.base_url, endpoint=url) as api:
            return api.get(header=self.headers)
    
    def get_area_by_id(self, area_id: int) -> Dict[str, Any]:
        """
        获取特定聚落信息
        
        通过聚落area_id获取已录入系统的绵中方块人服务器上特定聚落的详细信息
        
        Args:
            area_id: 聚落ID
            
        Returns:
            Dict[str, Any]: 包含特定聚落信息的响应数据
        """
        url = f"/api/v2/area/{area_id}/"
        with Get(base_url=self.base_url, endpoint=url) as api:
            return api.get(header=self.headers)


if __name__ == "__main__":
    client = EaverseAPIClient()

