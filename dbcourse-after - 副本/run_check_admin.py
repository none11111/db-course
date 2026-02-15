#!/usr/bin/env python3
"""
运行check_admin.py脚本并输出结果
"""

import subprocess
import sys

# 运行check_admin.py脚本
try:
    result = subprocess.run(
        [sys.executable, 'check_admin.py'],
        capture_output=True,
        text=True,
        cwd='c:\\Users\\18548\\Desktop\\dbcourse-after - 副本 (2)'
    )
    
    print("===== check_admin.py 脚本输出 =====")
    print("标准输出:")
    print(result.stdout)
    
    if result.stderr:
        print("标准错误:")
        print(result.stderr)
    
    print("返回代码:", result.returncode)
    
except Exception as e:
    print(f"运行脚本时出错: {str(e)}")