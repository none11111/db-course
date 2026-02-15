#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库设置脚本
用于创建数据库、重置表结构并生成测试数据
确保所有生成的内容都写入到指定的MySQL数据库中
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import Treet_IP_Conn, User, Post, Comment, Category, Tag
from app.utils.db_utils import init_test_data
from sqlalchemy import text

def setup_database():
    """设置数据库：创建表结构并生成测试数据"""
    app = create_app('development')
    
    with app.app_context():
        try:
            print("=" * 60)
            print("    论坛系统 - 数据库设置工具")
            print("=" * 60)
            print("正在连接到MySQL数据库...")
            
            # 测试数据库连接
            try:
                Treet_IP_Conn.engine.connect()
                print("✅ 成功连接到MySQL数据库")
                print(f"   数据库: forum_system")
                print(f"   主机: localhost")
                print(f"   用户: root")
                print(f"   字符集: utf8mb4")
            except Exception as e:
                print(f"❌ 数据库连接失败: {e}")
                print("请检查数据库配置和MySQL服务状态")
                return False
            
            print("\n1. 删除所有现有表...")
            # 先删除关联表
            try:
                Treet_IP_Conn.engine.execute(text("DROP TABLE IF EXISTS postcategories;"))
                Treet_IP_Conn.engine.execute(text("DROP TABLE IF EXISTS posttags;"))
                print("✅ 已删除关联表")
            except Exception as e:
                print(f"⚠️  删除关联表时出错: {e}")
            
            # 删除所有模型表
            Treet_IP_Conn.drop_all()
            print("✅ 已删除所有模型表")
            
            print("\n2. 重新创建表结构...")
            Treet_IP_Conn.create_all()
            print("✅ 表结构创建完成")
            
            print("\n3. 验证表结构...")
            inspector = Treet_IP_Conn.inspect(Treet_IP_Conn.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['users', 'posts', 'comments', 'categories', 'tags', 'postcategories', 'posttags']
            
            all_tables_exist = True
            for table in expected_tables:
                if table in tables:
                    print(f"✅ 表 '{table}' 已创建")
                else:
                    print(f"❌ 表 '{table}' 未创建")
                    all_tables_exist = False
            
            if not all_tables_exist:
                print("\n❌ 表结构验证失败")
                return False
            
            print("\n4. 生成测试数据...")
            init_test_data()
            print("✅ 测试数据生成完成")
            
            print("\n5. 验证数据生成...")
            user_count = User.query.count()
            post_count = Post.query.count()
            comment_count = Comment.query.count()
            category_count = Category.query.count()
            tag_count = Tag.query.count()
            
            print(f"   用户数: {user_count}")
            print(f"   帖子数: {post_count}")
            print(f"   评论数: {comment_count}")
            print(f"   分类数: {category_count}")
            print(f"   标签数: {tag_count}")
            
            if user_count > 0 and post_count > 0 and comment_count > 0:
                print("✅ 数据生成验证成功")
            else:
                print("⚠️  数据生成可能不完整")
            
            print("\n" + "=" * 60)
            print("数据库设置完成！")
            print("所有生成的内容已写入到指定的MySQL数据库中")
            print("数据库连接名称: Treet_IP_Conn")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ 数据库设置过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = setup_database()
    sys.exit(0 if success else 1)