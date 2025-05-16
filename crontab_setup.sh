#!/bin/bash

# macOS上设置crontab定时任务的脚本
# 用于设置每天凌晨2点执行理财产品抓取任务

# 获取脚本所在的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAILY_SCRIPT="${SCRIPT_DIR}/run_daily.sh"

# 设置crontab日志文件
CRON_LOG_DIR="$HOME/logs/financial_products_scraper/cron"
mkdir -p "$CRON_LOG_DIR"
CRON_LOG="$CRON_LOG_DIR/cron_execution_$(date +%Y%m%d).log"

# 检查run_daily.sh文件是否存在
if [ ! -f "$DAILY_SCRIPT" ]; then
    echo "错误: 未找到run_daily.sh文件。请确保该文件在当前目录中。"
    exit 1
fi

# 检查权限
if [ ! -x "$DAILY_SCRIPT" ]; then
    echo "给run_daily.sh添加执行权限..."
    chmod +x "$DAILY_SCRIPT"
fi

# 清除可能的扩展属性
echo "清除文件扩展属性以解决macOS权限问题..."
xattr -c "$DAILY_SCRIPT"

# 创建临时文件存储当前的crontab内容
TEMP_CRON=$(mktemp)
crontab -l > "$TEMP_CRON" 2>/dev/null

# 移除之前的任务（如果存在）
grep -v "理财产品抓取任务" "$TEMP_CRON" | grep -v "$DAILY_SCRIPT" > "${TEMP_CRON}.new"
mv "${TEMP_CRON}.new" "$TEMP_CRON"

# 添加新的定时任务
echo "# 理财产品抓取任务 - 每天凌晨2点执行" >> "$TEMP_CRON"
echo "0 2 * * * $DAILY_SCRIPT >> $CRON_LOG 2>&1" >> "$TEMP_CRON"

# 安装新的crontab
crontab "$TEMP_CRON"

echo "定时任务已成功设置为凌晨2:00执行。"
echo "crontab执行日志将保存到: $CRON_LOG"

# 清理临时文件
rm "$TEMP_CRON"

# 显示当前的crontab配置
echo ""
echo "当前的crontab配置如下:"
crontab -l

echo ""
echo "注意: 在macOS上，您可能需要允许cron访问磁盘的完全访问权限。"
echo "请前往 系统偏好设置 -> 安全性与隐私 -> 隐私 -> 完全磁盘访问权限"
echo "点击锁图标后点击+号，添加 /usr/sbin/cron 到列表中。"
echo ""
echo "如果仍然看到'Operation not permitted'错误，可能需要在系统设置中允许完全磁盘访问权限："
echo "1. 打开'系统设置' -> '隐私与安全性' -> '完全磁盘访问权限'"
echo "2. 添加终端(Terminal.app)和/usr/sbin/cron到列表中" 