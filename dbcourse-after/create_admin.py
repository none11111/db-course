#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建root管理员账号脚本
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Treet_IP_Conn, User, UserRole, UserStatus

def create_root_admin():
    """创建root管理员账号"""
    app = create_app()
    
    with app.app_context():
        # 检查root用户是否已存在
        root_user = User.query.filter_by(UserName='root').first()
        
        if root_user:
            print("✓ root管理员账号已存在")
            return
        
        try:
            # 创建root用户
            root = User(
                UserName='root',
                UserEmail='root@example.com',
                RegistrationDate=datetime.utcnow(),
                LastLoginTime=datetime.utcnow(),
                Status=UserStatus.ACTIVE,
                Role=UserRole.ADMIN,
                Reputation=0
            )
            root.set_password('123456')
            
            # 添加到数据库
            Treet_IP_Conn.session.add(root)
            Treet_IP_Conn.session.commit()
            
            print("✓ root管理员账号创建成功！")
            print("  用户名: root")
            print("  密码: 123456")
        except Exception as e:
            Treet_IP_Conn.session.rollback()
            print(f"✗ 创建root管理员账号失败: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_root_admin()