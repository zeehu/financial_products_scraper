from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Product(Base):
    """理财产品基本信息表"""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), unique=True, nullable=False, comment='产品ID')
    product_code = Column(String(50), index=True, comment='产品登记编码')
    product_name = Column(String(200), comment='产品名称')
    issuer = Column(String(100), comment='发行机构名称')
    issuer_code = Column(String(50), comment='发行机构代码')
    risk_level = Column(String(50), comment='风险等级描述')
    risk_level_code = Column(String(10), comment='风险等级代码')
    product_type = Column(String(50), comment='产品类型描述')
    product_type_code = Column(String(10), comment='产品类型代码')
    currency = Column(String(10), comment='币种')
    investment_period = Column(String(50), comment='投资期限')
    min_investment = Column(String(50), comment='起投金额')
    sale_status = Column(String(20), comment='销售状态')
    sale_regions = Column(Text, comment='销售区域')
    start_date = Column(String(20), comment='开始日期')
    end_date = Column(String(20), comment='结束日期')
    product_category = Column(String(50), comment='产品类别')
    income_type = Column(String(50), comment='收益类型')
    sale_method = Column(String(50), comment='销售方式')
    
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关联净值数据
    nav_records = relationship("ProductNav", back_populates="product")
    
    def __repr__(self):
        return f"<Product(product_code='{self.product_code}', product_name='{self.product_name}')>"


class ProductNav(Base):
    """理财产品净值信息表"""
    __tablename__ = 'product_navs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), ForeignKey('products.product_id'), nullable=False, comment='产品ID')
    product_code = Column(String(50), index=True, comment='产品登记编码')
    nav_date = Column(Date, nullable=False, comment='净值日期')
    initial_nav = Column(Float, comment='初始净值')
    accumulated_nav = Column(Float, comment='累计净值')
    current_nav = Column(Float, comment='当前净值')
    
    is_updated = Column(Integer, default=0, comment='是否更新(0:未更新,1:已更新)')
    last_update_date = Column(Date, comment='最近更新日期')
    
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关联产品信息
    product = relationship("Product", back_populates="nav_records")
    
    def __repr__(self):
        return f"<ProductNav(product_code='{self.product_code}', nav_date='{self.nav_date}')>" 