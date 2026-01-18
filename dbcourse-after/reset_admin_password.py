#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置管理员密码的脚本
"""
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

# 导入模型和配置
from app.models import Treet_IP_Conn, User
from app.models.user import UserRole, UserStatus

# 创建会话
Session = sessionmaker(bind=Treet_IP_Conn.engine)
session = Session()

try:
    # 查找管理员账号
    admin_user = session.query(User).filter_by(Role=UserRole.ADMIN).first()
    
    if admin_user:
        print(f"找到管理员账号: {admin_user.UserName}")
        
        # 设置新密码
        new_password = input("请输入新的管理员密码: ")
        if not new_password:
            print("密码不能为空")
            sys.exit(1)
        
        admin_user.set_password(new_password)
        admin_user.LastLoginTime = datetime.utcnow()
        
        session.commit()
        print(f"管理员密码已成功重置")
        print(f"用户名: {admin_user.UserName}")
        print(f"新密码: {new_password}")
    else:
        print("没有找到管理员账号")
        
        # 询问是否创建新的管理员账号
        create_new = input("是否创建新的管理员账号？(y/n): ")
        if create_new.lower() == 'y':
            username = input("请输入管理员用户名 (默认: admin): ") or 'admin'
            new_password = input("请输入管理员密码: ")
            
            if not new_password:
                print("密码不能为空")
                sys.exit(1)
            
            # 创建新管理员
            new_admin = User(
                UserName=username,
                UserEmail=None
            )
            new_admin.set_password(new_password)
            new_admin.Role = UserRole.ADMIN
            new_admin.Status = UserStatus.ACTIVE
            new_admin.Reputation = 100
            
            session.add(new_admin)
            session.commit()
            
            print(f"新管理员账号已创建")
            print(f"用户名: {new_admin.UserName}")
            print(f"密码: {new_password}")
    
except Exception as e:
    session.rollback()
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()