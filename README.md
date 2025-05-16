# 理财产品抓取工具

抓取中国财富网(chinawealth.com.cn)的理财产品信息和净值数据，并存储到数据库。

## 功能特点

- 抓取理财产品基本信息
- 抓取理财产品净值数据
- 存储数据到SQLite或MySQL数据库
- 智能错误处理和重试机制
- 支持数据导出(CSV/Excel)

## 安装

1. 克隆仓库后，创建虚拟环境：

```bash
python -m venv .venv
```

2. 激活虚拟环境：

在macOS/Linux上：
```bash
source .venv/bin/activate
```

在Windows上：
```bash
.venv\Scripts\activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 安装项目（开发模式）：

```bash
pip install -e .
```

## 使用方法

### 数据抓取

直接运行主脚本：

```bash
python run.py
```

可用参数：

```bash
python run.py --max-pages 10  # 限制抓取页数
python run.py --use-proxy     # 使用代理
```

### 数据导出

导出数据为CSV和Excel格式：

```bash
python export_data.py
```

可用参数：

```bash
python export_data.py --format csv    # 仅导出CSV格式
python export_data.py --format excel  # 仅导出Excel格式
python export_data.py --output-dir ./my_data  # 指定输出目录
```

## 配置

可以通过环境变量或创建.env文件配置：

- `DB_TYPE`: 数据库类型（sqlite或mysql），默认sqlite
- `LOG_LEVEL`: 日志级别，默认INFO
- `MAX_PAGES`: 最大抓取页数，默认不限制
- `USE_PROXY`: 是否使用代理，默认false
- `REQUEST_DELAY`: 请求延迟秒数，默认5秒

## 项目结构

```
financial_products_scraper/
├── data/                    # 数据目录
│   ├── db/                  # 数据库文件
│   ├── export/              # 数据导出目录
│   └── csv/                 # CSV文件目录
├── logs/                    # 日志目录 
├── src/                     # 源代码目录
│   ├── config/              # 配置模块
│   ├── database/            # 数据库模块
│   ├── models/              # 数据模型
│   ├── scrapers/            # 爬虫模块
│   └── utils/               # 工具模块
├── run.py                   # 运行脚本
├── export_data.py           # 数据导出脚本
├── requirements.txt         # 依赖文件
└── setup.py                 # 安装脚本
```

## 数据库模型

### 产品基本信息表（products）

包含理财产品的基本信息，如产品名称、发行机构、风险等级等。产品登记编码（product_code）作为唯一标识，用于关联查询。

主要字段：
- `product_code`: 产品登记编码（唯一标识）
- `product_name`: 产品名称
- `issuer`: 发行机构
- `risk_level`: 风险等级
- `product_type`: 产品类型
- `currency`: 币种
- `investment_period`: 投资期限
- `start_date`: 开始日期
- `end_date`: 结束日期

### 产品净值信息表（product_navs）

包含理财产品的净值信息，通过product_code与产品基本信息表关联。

主要字段：
- `product_code`: 产品登记编码（外键）
- `nav_date`: 净值日期
- `initial_nav`: 初始净值
- `accumulated_nav`: 累计净值
- `current_nav`: 当前净值
- `is_updated`: 是否更新(0:未更新,1:已更新)
- `last_update_date`: 最近更新日期

## 导出数据格式

### CSV导出

导出三个CSV文件：
- `products_[timestamp].csv`: 产品基本信息
- `navs_[timestamp].csv`: 产品净值信息
- `combined_[timestamp].csv`: 产品和净值的联合数据

### Excel导出

导出一个Excel文件，包含三个工作表：
- `产品基本信息`: 产品基本信息表
- `产品净值信息`: 产品净值信息表
- `产品完整数据`: 产品和净值的联合数据

## 许可证

MIT

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

## 贡献

欢迎提交 Issue 或 Pull Request 来完善本项目。 