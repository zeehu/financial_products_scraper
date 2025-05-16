# 理财产品信息抓取模块

__version__ = '0.1.0'

# 导出常用模块，简化导入路径
from src.config.config import setup_logging, get_database_url, get_scraper_config
from src.scrapers.chinawealth_scraper import ChinaWealthScraper 