from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date
import logging
import os
from typing import List, Dict, Optional, Any
from ..models.product import Base, Product, ProductNav

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, db_url: str = None):
        """初始化数据库连接"""
        if db_url is None:
            # 默认使用SQLite数据库
            db_dir = os.path.join(os.getcwd(), 'data', 'db')
            os.makedirs(db_dir, exist_ok=True)
            db_url = f"sqlite:///{os.path.join(db_dir, 'financial_products.db')}"
            
        self.engine = create_engine(db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        # 创建表
        Base.metadata.create_all(self.engine)
        logger.info(f"数据库初始化完成，使用: {db_url}")
        
    def get_session(self):
        """获取数据库会话"""
        return self.Session()
    
    def close(self):
        """关闭数据库连接"""
        self.Session.remove()
        
    def save_products(self, products: List[Dict]) -> int:
        """
        保存产品基本信息
        
        Args:
            products: 产品信息列表
            
        Returns:
            保存的产品数量
        """
        session = self.get_session()
        try:
            saved_count = 0
            for product_info in products:
                product_id = product_info.get('product_id')
                if not product_id:
                    logger.warning(f"产品信息缺少product_id: {product_info}")
                    continue
                    
                # 查找是否已存在
                product = session.query(Product).filter_by(product_id=product_id).first()
                
                if product:
                    # 更新已有产品信息
                    for key, value in product_info.items():
                        if hasattr(product, key) and key != 'product_id':
                            setattr(product, key, value)
                else:
                    # 创建新产品
                    product = Product(**product_info)
                    session.add(product)
                
                saved_count += 1
            
            session.commit()
            logger.info(f"成功保存 {saved_count} 条产品信息")
            return saved_count
        except Exception as e:
            session.rollback()
            logger.error(f"保存产品信息失败: {str(e)}")
            raise
        finally:
            session.close()
            
    def save_product_navs(self, navs: List[Dict]) -> int:
        """
        保存产品净值信息，并检查更新状态
        
        Args:
            navs: 净值信息列表
            
        Returns:
            保存的净值记录数量
        """
        session = self.get_session()
        try:
            saved_count = 0
            for nav_info in navs:
                product_id = nav_info.get('product_id')
                nav_date_str = nav_info.get('nav_date')
                
                if not product_id or not nav_date_str:
                    logger.warning(f"净值信息缺少必要字段: {nav_info}")
                    continue
                
                # 转换日期格式
                try:
                    nav_date = datetime.strptime(nav_date_str, "%Y-%m-%d").date()
                except ValueError:
                    logger.warning(f"净值日期格式错误: {nav_date_str}")
                    continue
                    
                # 查找是否已存在该日期的净值记录
                existing_nav = session.query(ProductNav).filter_by(
                    product_id=product_id, 
                    nav_date=nav_date
                ).first()
                
                if existing_nav:
                    # 检查净值是否有更新
                    is_updated = False
                    for nav_type in ['initial_nav', 'accumulated_nav', 'current_nav']:
                        old_value = getattr(existing_nav, nav_type)
                        new_value = nav_info.get(nav_type)
                        
                        if new_value is not None and old_value != new_value:
                            setattr(existing_nav, nav_type, new_value)
                            is_updated = True
                    
                    if is_updated:
                        existing_nav.is_updated = 1
                        existing_nav.last_update_date = date.today()
                else:
                    # 创建新净值记录
                    nav_record = ProductNav(
                        product_id=product_id,
                        product_code=nav_info.get('product_code'),
                        nav_date=nav_date,
                        initial_nav=nav_info.get('initial_nav'),
                        accumulated_nav=nav_info.get('accumulated_nav'),
                        current_nav=nav_info.get('current_nav'),
                        is_updated=0,  # 新记录默认为未更新
                        last_update_date=None
                    )
                    session.add(nav_record)
                
                saved_count += 1
                
            session.commit()
            logger.info(f"成功保存 {saved_count} 条净值信息")
            return saved_count
        except Exception as e:
            session.rollback()
            logger.error(f"保存净值信息失败: {str(e)}")
            raise
        finally:
            session.close()
            
    def get_products_count(self) -> int:
        """获取产品总数"""
        session = self.get_session()
        try:
            return session.query(Product).count()
        finally:
            session.close()
            
    def get_product_navs_count(self) -> int:
        """获取净值记录总数"""
        session = self.get_session()
        try:
            return session.query(ProductNav).count()
        finally:
            session.close() 