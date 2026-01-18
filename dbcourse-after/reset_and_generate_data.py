#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重置数据库并生成扶贫助农主题测试数据
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import Treet_IP_Conn, User, Post, Comment, Category, Tag
from app.utils.db_utils import init_test_data

def reset_database():
    """重置数据库"""
    print(f"[{datetime.now()}] 开始重置数据库...")
    
    # 创建Flask应用
    app = create_app()
    
    with app.app_context():
        try:
            # 删除所有评论
            Comment.query.delete()
            print(f"[{datetime.now()}] 已删除所有评论")
            
            # 删除所有帖子（需要先删除评论，因为有外键约束）
            Post.query.delete()
            print(f"[{datetime.now()}] 已删除所有帖子")
            
            # 注意：这里不删除用户、分类和标签，以便保留基本结构
            
            # 提交更改
            Treet_IP_Conn.session.commit()
            print(f"[{datetime.now()}] 数据库重置完成")
            
        except Exception as e:
            Treet_IP_Conn.session.rollback()
            print(f"[{datetime.now()}] 数据库重置失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def generate_test_data():
    """生成测试数据"""
    print(f"[{datetime.now()}] 开始生成测试数据...")
    
    # 创建Flask应用
    app = create_app()
    
    with app.app_context():
        try:
            # 生成测试数据
            init_test_data()
            print(f"[{datetime.now()}] 测试数据生成完成")
            
        except Exception as e:
            print(f"[{datetime.now()}] 测试数据生成失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def check_database_connection():
    """检查数据库连接"""
    print(f"[{datetime.now()}] 开始检查数据库连接...")
    
    # 创建Flask应用
    app = create_app()
    
    with app.app_context():
        try:
            # 测试数据库连接
            Treet_IP_Conn.session.execute('SELECT 1')
            print(f"[{datetime.now()}] 数据库连接正常")
            
            # 查询一些基本信息
            user_count = User.query.count()
            post_count = Post.query.count()
            comment_count = Comment.query.count()
            category_count = Category.query.count()
            tag_count = Tag.query.count()
            
            print(f"[{datetime.now()}] 数据库统计:")
            print(f"  - 用户数: {user_count}")
            print(f"  - 帖子数: {post_count}")
            print(f"  - 评论数: {comment_count}")
            print(f"  - 分类数: {category_count}")
            print(f"  - 标签数: {tag_count}")
            
            return True
            
        except Exception as e:
            print(f"[{datetime.now()}] 数据库连接失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("    扶贫助农论坛 - 数据库重置与数据生成工具")
    print("=" * 60)
    
    # 检查数据库连接
    if not check_database_connection():
        print("数据库连接失败，请检查配置后重试")
        return 1
    
    # 重置数据库
    if not reset_database():
        print("数据库重置失败，请检查错误后重试")
        return 1
    
    # 生成测试数据
    if not generate_test_data():
        print("测试数据生成失败，请检查错误后重试")
        return 1
    
    # 再次检查数据库状态
    print("\n" + "=" * 60)
    print("    操作完成后的数据库状态")
    print("=" * 60)
    check_database_connection()
    
    print("\n" + "=" * 60)
    print("所有操作完成！论坛现在应该显示扶贫助农相关内容")
    print("=" * 60)
    return 0

if __name__ == '__main__':
    sys.exit(main())