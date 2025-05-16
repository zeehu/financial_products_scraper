# 中国财富网理财产品数据抓取工具

## 项目简介

该项目用于抓取中国财富网(chinawealth.com.cn)的理财产品基本信息和净值数据，将数据存储到本地数据库中，便于查询和分析。

## 功能特点

- 支持抓取中国财富网理财产品基本信息和净值数据
- 将数据分别存储到两个表中，并支持关联查询
- 自动比对净值数据，记录更新状态
- 支持命令行参数配置，方便灵活使用
- 完善的日志记录和错误处理机制
- 支持SQLite和MySQL数据库存储

## 技术栈

- Python 3.7+
- SQLAlchemy (数据库ORM)
- Requests (HTTP请求库)
- BeautifulSoup4 (HTML解析)
- Pandas (数据处理)

## 安装使用

### 1. 克隆项目
```bash
git clone https://github.com/zeehu/financial_products_scraper.git
cd financial_products_scraper
```

### 2. 创建虚拟环境
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
# 复制环境变量示例文件
cp .env.example .env
# 根据需要编辑.env文件
```

### 5. 运行程序
```bash
python run.py
```

## 命令行参数

程序支持以下命令行参数：

- `--max-pages`: 限制最大抓取页数，默认不限制
- `--use-proxy`: 使用代理服务器（需自行配置代理获取逻辑）

示例：
```bash
# 抓取前5页数据
python run.py --max-pages 5

# 使用代理抓取
python run.py --use-proxy
```

## 数据库设计

### 产品基本信息表(products)

| 字段名 | 类型 | 说明 |
|-------|------|-----|
| id | Integer | 自增主键 |
| product_id | String | 产品ID (唯一) |
| product_code | String | 产品登记编码 |
| product_name | String | 产品名称 |
| issuer | String | 发行机构 |
| issuer_code | String | 发行机构代码 |
| risk_level | String | 风险等级描述 |
| risk_level_code | String | 风险等级代码 |
| product_type | String | 产品类型描述 |
| product_type_code | String | 产品类型代码 |
| currency | String | 币种 |
| investment_period | String | 投资期限 |
| min_investment | String | 起投金额 |
| sale_status | String | 销售状态 |
| sale_regions | Text | 销售区域 |
| start_date | String | 开始日期 |
| end_date | String | 结束日期 |
| product_category | String | 产品类别 |
| income_type | String | 收益类型 |
| sale_method | String | 销售方式 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 产品净值信息表(product_navs)

| 字段名 | 类型 | 说明 |
|-------|------|-----|
| id | Integer | 自增主键 |
| product_id | String | 产品ID (外键) |
| product_code | String | 产品登记编码 |
| nav_date | Date | 净值日期 |
| initial_nav | Float | 初始净值 |
| accumulated_nav | Float | 累计净值 |
| current_nav | Float | 当前净值 |
| is_updated | Integer | 是否更新(0:未更新,1:已更新) |
| last_update_date | Date | 最近更新日期 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## 项目结构

```
financial_products_scraper/
│
├── src/                        # 源代码目录
│   ├── config/                # 配置模块
│   │   ├── __init__.py
│   │   └── config.py          # 配置管理
│   │
│   ├── database/              # 数据库模块
│   │   ├── __init__.py
│   │   └── db_manager.py      # 数据库管理器
│   │
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   └── product.py         # 产品和净值模型
│   │
│   ├── scrapers/              # 爬虫模块
│   │   ├── __init__.py
│   │   ├── base_scraper.py    # 爬虫基类
│   │   └── chinawealth_scraper.py # 中国财富网爬虫
│   │
│   ├── utils/                 # 工具模块
│   │   └── __init__.py
│   │
│   ├── __init__.py
│   └── main.py                # 主程序
│
├── data/                       # 数据目录
│   ├── db/                    # 数据库文件
│   ├── debug/                 # 调试信息
│   └── csv/                   # CSV数据文件
│
├── logs/                       # 日志目录
├── .env.example                # 环境变量示例
├── requirements.txt            # 依赖列表
├── run.py                      # 入口脚本
└── README.md                   # 项目说明
```

## 注意事项

- 本项目仅用于学习和研究，请勿用于商业用途
- 爬取数据时请遵守网站的robots协议
- 请合理设置请求间隔，避免对目标网站造成压力

## 许可证

MIT

## 贡献

欢迎提交 Issue 或 Pull Request 来完善本项目。