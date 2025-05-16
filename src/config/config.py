import os
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 日志配置
def setup_logging(log_level=None):
    """配置日志"""
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 创建日志目录
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 配置日志格式
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'app.log')),
            logging.StreamHandler()
        ]
    )
    
    # 设置第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

# 数据库配置
def get_database_url():
    """获取数据库连接URL"""
    db_type = os.getenv('DB_TYPE', 'sqlite')
    
    if db_type.lower() == 'sqlite':
        db_dir = os.path.join(os.getcwd(), 'data', 'db')
        os.makedirs(db_dir, exist_ok=True)
        return f"sqlite:///{os.path.join(db_dir, 'financial_products.db')}"
    elif db_type.lower() == 'mysql':
        db_user = os.getenv('DB_USER', 'root')
        db_pass = os.getenv('DB_PASS', '')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '3306')
        db_name = os.getenv('DB_NAME', 'financial_products')
        return f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    else:
        raise ValueError(f"不支持的数据库类型: {db_type}")

# 爬虫配置
def get_scraper_config():
    """获取爬虫配置"""
    return {
        'max_pages': int(os.getenv('MAX_PAGES', '0')),  # 0表示不限制
        'use_proxy': os.getenv('USE_PROXY', 'false').lower() == 'true',
        'request_delay': float(os.getenv('REQUEST_DELAY', '5')),
        'retry_times': int(os.getenv('RETRY_TIMES', '5')),
        'timeout': int(os.getenv('REQUEST_TIMEOUT', '30')),
    } 