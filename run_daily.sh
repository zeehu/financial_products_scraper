#!/bin/bash

# 理财产品抓取定时任务脚本
# 用于每天凌晨2点执行抓取任务并导出数据
# 适用于macOS系统

# 设置日志文件
CRON_LOG_DIR="$HOME/logs/financial_products_scraper/crontab"
APP_LOG_DIR="$HOME/logs/financial_products_scraper/app"
CRON_LOG_FILE="$CRON_LOG_DIR/crontab_$(date +%Y%m%d).log"
APP_LOG_FILE="$APP_LOG_DIR/scraper_$(date +%Y%m%d).log"

# 设置项目路径（请根据实际情况修改）
PROJECT_DIR="/Users/jezee/Code/financial_products_scraper"

# 创建日志目录
mkdir -p "$CRON_LOG_DIR"
mkdir -p "$APP_LOG_DIR"

# 记录开始时间和系统信息
START_TIME=$(date +%s)
echo "=== 理财产品抓取任务开始执行 - $(date) ===" >> "$CRON_LOG_FILE"
echo "系统信息: $(uname -a)" >> "$CRON_LOG_FILE"
echo "脚本执行路径: $PROJECT_DIR" >> "$CRON_LOG_FILE"
echo "当前用户: $(whoami)" >> "$CRON_LOG_FILE"
echo "" >> "$CRON_LOG_FILE"

# 激活虚拟环境（如果使用了虚拟环境）
if [ -d "$PROJECT_DIR/.venv" ]; then
    echo "激活虚拟环境..." >> "$CRON_LOG_FILE"
    source "$PROJECT_DIR/.venv/bin/activate"
    echo "Python版本: $(python --version 2>&1)" >> "$CRON_LOG_FILE"
    PYTHON_CMD="python"  # 使用虚拟环境中的Python
else
    PYTHON_CMD="/usr/bin/python3"  # 使用系统Python作为备选
fi

# 检查并安装依赖
echo "检查项目依赖..." >> "$CRON_LOG_FILE"
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "安装依赖包..." >> "$CRON_LOG_FILE"
    $PYTHON_CMD -m pip install -r "$PROJECT_DIR/requirements.txt" >> "$CRON_LOG_FILE" 2>&1
    echo "依赖安装完成" >> "$CRON_LOG_FILE"
else
    # 如果没有requirements.txt，至少安装必要的包
    echo "未找到requirements.txt，安装基本依赖..." >> "$CRON_LOG_FILE"
    $PYTHON_CMD -m pip install python-dotenv requests sqlalchemy >> "$CRON_LOG_FILE" 2>&1
fi

# 进入项目目录
cd "$PROJECT_DIR" || {
    echo "切换到项目目录失败: $PROJECT_DIR" >> "$CRON_LOG_FILE"
    exit 1
}

# 执行抓取任务
echo "开始抓取理财产品数据 - $(date +%H:%M:%S)" >> "$CRON_LOG_FILE"
# 这里将应用日志重定向到应用日志文件
$PYTHON_CMD run.py > "$APP_LOG_FILE" 2>&1
SCRAPER_EXIT_CODE=$?

# 检查抓取任务是否成功
if [ $SCRAPER_EXIT_CODE -eq 0 ]; then
    echo "抓取任务执行成功 - $(date +%H:%M:%S)" >> "$CRON_LOG_FILE"
    
    # 导出数据为CSV和Excel格式
    echo "开始导出数据 - $(date +%H:%M:%S)" >> "$CRON_LOG_FILE"
    $PYTHON_CMD export_data.py --format all >> "$CRON_LOG_FILE" 2>&1
    EXPORT_EXIT_CODE=$?
    
    if [ $EXPORT_EXIT_CODE -eq 0 ]; then
        echo "数据导出成功 - $(date +%H:%M:%S)" >> "$CRON_LOG_FILE"
    else
        echo "数据导出失败，退出代码: $EXPORT_EXIT_CODE" >> "$CRON_LOG_FILE"
    fi
else
    echo "抓取任务执行失败，退出代码: $SCRAPER_EXIT_CODE" >> "$CRON_LOG_FILE"
    # 将错误日志的最后20行复制到crontab日志中
    echo "错误日志片段:" >> "$CRON_LOG_FILE"
    tail -20 "$APP_LOG_FILE" >> "$CRON_LOG_FILE"
fi

# 如果使用了虚拟环境，退出虚拟环境
if [ -d "$PROJECT_DIR/.venv" ]; then
    deactivate
fi

# 记录磁盘使用情况
echo "" >> "$CRON_LOG_FILE"
echo "数据目录磁盘使用情况:" >> "$CRON_LOG_FILE"
du -sh "$PROJECT_DIR/data" >> "$CRON_LOG_FILE" 2>&1

# 记录结束时间
END_TIME=$(date +%s)
ELAPSED_TIME=$((END_TIME - START_TIME))
echo "=== 理财产品抓取任务结束 - $(date) ===" >> "$CRON_LOG_FILE"
echo "任务总耗时: ${ELAPSED_TIME} 秒" >> "$CRON_LOG_FILE"
echo "" >> "$CRON_LOG_FILE" 
