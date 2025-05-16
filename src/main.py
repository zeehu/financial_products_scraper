import logging
import argparse
import time
from datetime import datetime

from src import setup_logging, get_database_url, get_scraper_config, ChinaWealthScraper
from src.database import DatabaseManager

logger = logging.getLogger(__name__)

def main():
    """主程序入口
    
    负责解析命令行参数、初始化组件、执行爬虫任务并保存数据。
    支持设置最大抓取页数和是否使用代理。
    """
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='理财产品信息抓取工具')
    parser.add_argument('--max-pages', type=int, default=None, 
                        help='最大抓取页数，默认为不限制')
    parser.add_argument('--use-proxy', action='store_true', 
                        help='是否使用代理')
    parser.add_argument('--product-code', type=str, default=None,
                        help='指定抓取单个产品，使用产品登记编码')
    args = parser.parse_args()
    
    # 初始化日志
    setup_logging()
    
    # 程序开始时间
    start_time = time.time()
    logger.info(f"抓取程序开始运行：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 获取配置
        config = get_scraper_config()
        
        # 命令行参数优先
        max_pages = args.max_pages if args.max_pages is not None else config['max_pages']
        use_proxy = args.use_proxy if args.use_proxy else config['use_proxy']
        
        # 初始化数据库
        db_url = get_database_url()
        db_manager = DatabaseManager(db_url)
        
        # 初始化爬虫
        scraper = ChinaWealthScraper(
            use_proxy=use_proxy, 
            retry_times=config['retry_times'],
            timeout=config['timeout'],
            request_delay=config['request_delay']
        )
        
        # 执行爬取
        if args.product_code:
            # 单个产品抓取模式
            logger.info(f"开始抓取指定产品的数据，产品登记编码: {args.product_code}")
            # 这里需要添加单个产品抓取的逻辑
            logger.warning("单个产品抓取功能尚未实现")
            products, navs = [], []
        else:
            # 批量抓取模式
            logger.info(f"开始抓取中国财富网理财产品数据 (最大页数: {max_pages if max_pages else '不限制'})")
            products, navs = scraper.scrape(max_pages=max_pages)
        
        # 保存数据到数据库
        if products:
            db_manager.save_products(products)
            logger.info(f"成功保存 {len(products)} 条产品基本信息")
        
        if navs:
            db_manager.save_product_navs(navs)
            logger.info(f"成功保存 {len(navs)} 条产品净值数据")
        
        # 获取数据库统计
        products_count = db_manager.get_products_count()
        navs_count = db_manager.get_product_navs_count()
        logger.info(f"数据库中共有 {products_count} 条产品信息，{navs_count} 条净值记录")
        
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
    finally:
        # 关闭数据库连接
        if 'db_manager' in locals():
            db_manager.close()
        
        # 计算运行时间
        elapsed_time = time.time() - start_time
        logger.info(f"程序运行完成，耗时 {elapsed_time:.2f} 秒")

if __name__ == "__main__":
    main() 