import requests
from typing import Any, Dict, Optional
from .exceptions import CNBAPIError
from .cnb import CNBServices

class CNBClient():
    """CNB OpenAPI 客户端"""
    
    def __init__(
        self,
        base_url: str = "https://api.cnb.cool",
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        初始化客户端
        
        :param base_url: API基础URL
        :param api_key: API密钥
        :param timeout: 请求超时时间(秒)
        :param max_retries: 最大重试次数
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # 配置默认请求头
        self.session.headers.update({
            "Accept": "application/vnd.cnb.api+json",
            "Content-Type": "application/json",
            "User-Agent": "python-cnb/1.0"
        })
        
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
        
        self.cnb = CNBServices(self)

    def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送API请求
        
        :param method: HTTP方法(GET, POST等)
        :param endpoint: API端点路径
        :param kwargs: 其他请求参数
        :return: 响应数据
        :raises: CNBAPIError 当API请求失败时
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # 设置默认超时
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
            
        try:
            response = self.session.request(
                method,
                url,
                **kwargs
            )
            response.raise_for_status()
            if not response.text.strip():
                return None
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            raise CNBAPIError(
                detail=e.response.text,
                status_code=status_code
            ) from e
        except requests.exceptions.RequestException as e:
            raise CNBAPIError(f"Request failed: {str(e)}") from e