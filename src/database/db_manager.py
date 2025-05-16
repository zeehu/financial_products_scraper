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
    """数据库管理类
    
    负责数据库连接管理、会话创建以及数据的增删改查操作。
    支持SQLite和MySQL数据库。
    """
    
    def __init__(self, db_url: str = None):
        """初始化数据库连接
        
        Args:
            db_url: 数据库连接URL，如为None则使用默认的SQLite数据库
        """
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
        """获取数据库会话
        
        Returns:
            SQLAlchemy会话对象
        """
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
                product_code = product_info.get('product_code')
                if not product_code:
                    logger.warning(f"产品信息缺少product_code: {product_info}")
                    continue
                    
                # 查找是否已存在(使用product_code作为唯一标识)
                product = session.query(Product).filter_by(product_code=product_code).first()
                
                if product:
                    # 更新已有产品信息
                    for key, value in product_info.items():
                        if hasattr(product, key) and key != 'product_code':
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
            updated_count = 0
            new_count = 0
            
            for nav_info in navs:
                product_code = nav_info.get('product_code')
                nav_date_str = nav_info.get('nav_date')
                
                if not product_code or not nav_date_str:
                    logger.warning(f"净值信息缺少必要字段: {nav_info}")
                    continue
                
                # 转换日期格式
                try:
                    nav_date = datetime.strptime(nav_date_str, "%Y-%m-%d").date()
                except ValueError:
                    logger.warning(f"净值日期格式错误: {nav_date_str}")
                    continue
                    
                # 查找是否已存在该日期的净值记录(使用product_code和nav_date作为组合唯一标识)
                existing_nav = session.query(ProductNav).filter_by(
                    product_code=product_code, 
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
                        updated_count += 1
                else:
                    # 创建新净值记录
                    nav_record = ProductNav(
                        product_id=nav_info.get('product_id'),
                        product_code=product_code,
                        nav_date=nav_date,
                        initial_nav=nav_info.get('initial_nav'),
                        accumulated_nav=nav_info.get('accumulated_nav'),
                        current_nav=nav_info.get('current_nav'),
                        is_updated=0,  # 新记录默认为未更新
                        last_update_date=None,
                        crawl_time=nav_info.get('crawl_time')
                    )
                    session.add(nav_record)
                    new_count += 1
                
                saved_count += 1
                
            session.commit()
            logger.info(f"成功保存 {saved_count} 条净值信息(新增: {new_count}, 更新: {updated_count})")
            return saved_count
        except Exception as e:
            session.rollback()
            logger.error(f"保存净值信息失败: {str(e)}")
            raise
        finally:
            session.close()
            
    def get_products_count(self) -> int:
        """获取产品总数
        
        Returns:
            数据库中产品记录的总数
        """
        session = self.get_session()
        try:
            return session.query(Product).count()
        finally:
            session.close()
            
    def get_product_navs_count(self) -> int:
        """获取净值记录总数
        
        Returns:
            数据库中净值记录的总数
        """
        session = self.get_session()
        try:
            return session.query(ProductNav).count()
        finally:
            session.close()
            
    def get_product_by_code(self, product_code: str) -> Optional[Product]:
        """根据产品登记编码获取产品信息
        
        Args:
            product_code: 产品登记编码
            
        Returns:
            产品信息对象，如不存在则返回None
        """
        session = self.get_session()
        try:
            return session.query(Product).filter_by(product_code=product_code).first()
        finally:
            session.close()
            
    def get_latest_nav_by_code(self, product_code: str) -> Optional[ProductNav]:
        """获取产品最新的净值信息
        
        Args:
            product_code: 产品登记编码
            
        Returns:
            最新的净值信息对象，如不存在则返回None
        """
        session = self.get_session()
        try:
            return session.query(ProductNav).filter_by(
                product_code=product_code
            ).order_by(ProductNav.nav_date.desc()).first()
        finally:
            session.close() 