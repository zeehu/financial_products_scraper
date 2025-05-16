#!/bin/bash

# 理财产品抓取定时任务脚本
# 用于每天凌晨2点执行抓取任务并导出数据
# 适用于macOS系统

# 设置日志文件
LOG_DIR="$HOME/logs/financial_products_scraper"
LOG_FILE="$LOG_DIR/scraper_$(date +%Y%m%d).log"

# 设置项目路径（请根据实际情况修改）
PROJECT_DIR="/Users/jezee/Desktop/cursor-code/financial_products_scraper"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 记录开始时间和系统信息
START_TIME=$(date +%s)
echo "=== 理财产品抓取任务开始执行 - $(date) ===" >> "$LOG_FILE"
echo "系统信息: $(uname -a)" >> "$LOG_FILE"
echo "脚本执行路径: $PROJECT_DIR" >> "$LOG_FILE"
echo "当前用户: $(whoami)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 激活虚拟环境（如果使用了虚拟环境）
if [ -d "$PROJECT_DIR/.venv" ]; then
    echo "激活虚拟环境..." >> "$LOG_FILE"
    source "$PROJECT_DIR/.venv/bin/activate"
    echo "Python版本: $(python --version 2>&1)" >> "$LOG_FILE"
fi

# 进入项目目录
cd "$PROJECT_DIR" || {
    echo "切换到项目目录失败: $PROJECT_DIR" >> "$LOG_FILE"
    exit 1
}

# 执行抓取任务
echo "开始抓取理财产品数据 - $(date +%H:%M:%S)" >> "$LOG_FILE"
python run.py --max-pages 6 >> "$LOG_FILE" 2>&1
SCRAPER_EXIT_CODE=$?

# 检查抓取任务是否成功
if [ $SCRAPER_EXIT_CODE -eq 0 ]; then
    echo "抓取任务执行成功 - $(date +%H:%M:%S)" >> "$LOG_FILE"
    
    # 导出数据为CSV和Excel格式
    echo "开始导出数据 - $(date +%H:%M:%S)" >> "$LOG_FILE"
    python export_data.py --format all >> "$LOG_FILE" 2>&1
    EXPORT_EXIT_CODE=$?
    
    if [ $EXPORT_EXIT_CODE -eq 0 ]; then
        echo "数据导出成功 - $(date +%H:%M:%S)" >> "$LOG_FILE"
    else
        echo "数据导出失败，退出代码: $EXPORT_EXIT_CODE" >> "$LOG_FILE"
    fi
else
    echo "抓取任务执行失败，退出代码: $SCRAPER_EXIT_CODE" >> "$LOG_FILE"
fi

# 如果使用了虚拟环境，退出虚拟环境
if [ -d "$PROJECT_DIR/.venv" ]; then
    deactivate
fi

# 记录磁盘使用情况
echo "" >> "$LOG_FILE"
echo "数据目录磁盘使用情况:" >> "$LOG_FILE"
du -sh "$PROJECT_DIR/data" >> "$LOG_FILE" 2>&1

# 记录结束时间
END_TIME=$(date +%s)
ELAPSED_TIME=$((END_TIME - START_TIME))
echo "=== 理财产品抓取任务结束 - $(date) ===" >> "$LOG_FILE"
echo "任务总耗时: ${ELAPSED_TIME} 秒" >> "$LOG_FILE"
echo "" >> "$LOG_FILE" 