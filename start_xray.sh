#!/bin/bash
set -e

# تولید مسیرهای تصادفی اگر وجود ندارند
if [ ! -f /data/paths.json ]; then
    python /app/genpaths.py
fi

# بارگذاری مسیرها
source_paths=$(cat /data/paths.json | python -c "import sys, json; print(json.load(sys.stdin))")

# اجرای Xray با کانفیگ نهایی
# فرض بر این است که اسکریپت generate_config.py کانفیگ نهایی را در /etc/xray/config.json می‌سازد
python /app/generate_config.py

xray run -c /etc/xray/config.json