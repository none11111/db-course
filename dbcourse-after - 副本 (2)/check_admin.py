#!/usr/bin/env python3
"""
检查管理员账号状态并创建管理员账号（如果不存在）
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import db, User
from app.models.user import UserRole, UserStatus

def check_admin_account():
    """检查管理员账号状态并创建（如果不存在）"""
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        try:
            # 查询所有管理员账号
            admins = User.query.filter_by(Role=UserRole.ADMIN).all()
            
            if admins:
                print("管理员账号列表：")
                for admin in admins:
                    print(f"用户名: {admin.UserName}, ID: {admin.UserID}, 状态: {admin.Status.value}, 角色: {admin.Role.value}, 最后登录时间: {admin.LastLoginTime}")
                    print(f"密码哈希: {admin.PasswordHash}")
                    print(f"是否激活: {admin.is_active()}")
                    print("-" * 50)
            else:
                print("没有找到管理员账号，正在创建...")
                
                # 创建新的管理员账号
                admin_user = User(
                    UserName='admin',
                    Status=UserStatus.ACTIVE,
                    Role=UserRole.ADMIN
                )
                admin_user.set_password('admin123')  # 设置默认密码
                
                db.session.add(admin_user)
                db.session.commit()
                
                print("管理员账号创建成功！")
                print(f"用户名: admin")
                print(f"密码: admin123")
                print("请登录后及时修改密码！")
                
        except Exception as e:
            print(f"检查或创建管理员账号时出错: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_admin_account()