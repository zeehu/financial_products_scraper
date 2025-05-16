#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据导出工具
用于将数据库中的理财产品数据导出为CSV或Excel格式
"""

import os
import argparse
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

from src.config.config import setup_logging, get_database_url

logger = logging.getLogger(__name__)

class DataExporter:
    """数据导出工具类
    
    用于将数据库中存储的理财产品数据导出为CSV或Excel格式，
    支持导出产品基本信息、净值信息以及联合查询数据。
    """

    def __init__(self, db_url=None, output_dir=None):
        """
        初始化数据导出器
        
        Args:
            db_url: 数据库连接URL，默认使用配置文件中的设置
            output_dir: 输出目录，默认为'data/export'
        """
        self.db_url = db_url or get_database_url()
        
        # 创建数据库引擎
        self.engine = create_engine(self.db_url)
        
        # 设置输出目录
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'data', 'export')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 当前时间戳（用于文件名）
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        logger.info(f"数据导出工具初始化完成，输出目录: {self.output_dir}")
        
    def _get_products_data(self):
        """获取产品基本信息数据
        
        Returns:
            产品基本信息的DataFrame
        """
        query = """
        SELECT 
            p.id, p.product_id, p.product_code, p.product_name, 
            p.issuer, p.issuer_code, p.risk_level, p.risk_level_code,
            p.product_type, p.product_type_code, p.currency, 
            p.investment_period, p.min_investment, p.sale_status,
            p.sale_regions, p.start_date, p.end_date, 
            p.product_category, p.income_type, p.sale_method,
            p.crawl_time, p.created_at, p.updated_at
        FROM 
            products p
        ORDER BY 
            p.product_code, p.id
        """
        return pd.read_sql(text(query), self.engine)
    
    def _get_navs_data(self):
        """获取产品净值数据
        
        Returns:
            产品净值数据的DataFrame
        """
        query = """
        SELECT 
            n.id, n.product_id, n.product_code, p.product_name,
            n.nav_date, n.initial_nav, n.accumulated_nav, n.current_nav,
            n.is_updated, n.last_update_date, n.crawl_time,
            n.created_at, n.updated_at
        FROM 
            product_navs n
        LEFT JOIN
            products p ON n.product_code = p.product_code
        ORDER BY 
            n.product_code, n.nav_date DESC
        """
        return pd.read_sql(text(query), self.engine)
    
    def _get_combined_data(self):
        """获取产品与净值的联合数据
        
        Returns:
            产品信息与净值数据关联后的DataFrame
        """
        query = """
        SELECT 
            p.product_id, p.product_code, p.product_name, 
            p.issuer, p.risk_level, p.product_type,
            p.currency, p.investment_period, p.min_investment,
            p.start_date, p.end_date, p.product_category,
            p.income_type, n.nav_date, n.initial_nav, 
            n.accumulated_nav, n.current_nav
        FROM 
            products p
        LEFT JOIN
            product_navs n ON p.product_code = n.product_code
        ORDER BY 
            p.product_code, n.nav_date DESC
        """
        return pd.read_sql(text(query), self.engine)
    
    def export_to_csv(self):
        """导出数据到CSV文件
        
        Returns:
            包含导出文件路径的字典
        """
        # 导出产品基本信息
        products_df = self._get_products_data()
        products_file = os.path.join(self.output_dir, f'products_{self.timestamp}.csv')
        products_df.to_csv(products_file, index=False, encoding='utf-8-sig')
        logger.info(f"成功导出 {len(products_df)} 条产品信息到 {products_file}")
        
        # 导出净值数据
        navs_df = self._get_navs_data()
        navs_file = os.path.join(self.output_dir, f'navs_{self.timestamp}.csv')
        navs_df.to_csv(navs_file, index=False, encoding='utf-8-sig')
        logger.info(f"成功导出 {len(navs_df)} 条净值信息到 {navs_file}")
        
        # 导出联合数据
        combined_df = self._get_combined_data()
        combined_file = os.path.join(self.output_dir, f'combined_{self.timestamp}.csv')
        combined_df.to_csv(combined_file, index=False, encoding='utf-8-sig')
        logger.info(f"成功导出 {len(combined_df)} 条联合数据到 {combined_file}")
        
        return {
            'products': products_file,
            'navs': navs_file,
            'combined': combined_file
        }
    
    def export_to_excel(self):
        """导出数据到Excel文件
        
        Returns:
            Excel文件路径
        """
        excel_file = os.path.join(self.output_dir, f'financial_products_{self.timestamp}.xlsx')
        
        # 创建Excel写入器
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # 导出产品基本信息
            products_df = self._get_products_data()
            products_df.to_excel(writer, sheet_name='产品基本信息', index=False)
            
            # 导出净值数据
            navs_df = self._get_navs_data()
            navs_df.to_excel(writer, sheet_name='产品净值信息', index=False)
            
            # 导出联合数据
            combined_df = self._get_combined_data()
            combined_df.to_excel(writer, sheet_name='产品完整数据', index=False)
        
        logger.info(f"成功导出所有数据到Excel文件: {excel_file}")
        return excel_file

def main():
    """脚本入口函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='理财产品数据导出工具')
    parser.add_argument('--format', choices=['csv', 'excel', 'all'], default='all',
                        help='导出格式，可选csv/excel/all，默认为all')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='输出目录，默认为data/export')
    args = parser.parse_args()
    
    # 初始化日志
    setup_logging()
    
    # 开始导出
    start_time = datetime.now()
    logger.info(f"开始导出数据: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 初始化导出器
        exporter = DataExporter(output_dir=args.output_dir)
        
        # 根据指定格式导出
        if args.format in ['csv', 'all']:
            csv_files = exporter.export_to_csv()
            logger.info(f"CSV文件导出完成: {csv_files}")
            
        if args.format in ['excel', 'all']:
            excel_file = exporter.export_to_excel()
            logger.info(f"Excel文件导出完成: {excel_file}")
            
    except Exception as e:
        logger.error(f"导出数据时出错: {str(e)}")
    finally:
        # 计算耗时
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"数据导出完成，共耗时 {elapsed_time:.2f} 秒")

if __name__ == "__main__":
    main() 