import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """爬虫基类"""
    
    def __init__(self, 
                 use_proxy: bool = False,
                 retry_times: int = 5,
                 timeout: int = 30,
                 request_delay: float = 5.0):
        """
        初始化爬虫基类
        
        Args:
            use_proxy: 是否使用代理
            retry_times: 重试次数
            timeout: 请求超时时间(秒)
            request_delay: 请求延迟(秒)
        """
        self.session = requests.Session()
        
        # 设置重试策略
        retry_strategy = Retry(
            total=retry_times,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504, 429],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 基本配置
        self.timeout = timeout
        self.request_delay = request_delay
        self.use_proxy = use_proxy
        self.proxies = self._get_proxy() if use_proxy else None
        
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Edge/122.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
        ]
        return random.choice(user_agents)
        
    def _get_proxy(self) -> Dict[str, str]:
        """获取代理配置（需要子类实现具体的代理获取逻辑）"""
        # 默认返回空代理
        return {}
    
    def _wait(self, retry_count: int = 0):
        """请求等待，避免频繁请求"""
        base_delay = self.request_delay
        delay = base_delay + (retry_count * 2) + random.uniform(1, 3)
        logger.debug(f"等待 {delay:.1f} 秒后发起请求...")
        time.sleep(delay)
        
    @abstractmethod
    def scrape(self, **kwargs) -> Tuple[List[Dict], List[Dict]]:
        """
        执行爬取任务，返回抓取到的产品信息和净值信息
        
        Returns:
            (产品基本信息列表, 产品净值信息列表)
        """
        pass 