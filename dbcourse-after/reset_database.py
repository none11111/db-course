#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库重置脚本
用于清理现有的数据库表结构并重新创建符合模型定义的表
"""

from app import create_app
from app.models import Treet_IP_Conn

# 创建应用实例
app = create_app()

with app.app_context():
    print("=== 数据库重置脚本 ===")
    print("注意：此操作将删除所有现有数据并重新创建表结构！")
    
    try:
            # 1. 先删除所有表（包括关联表）
            print("\n1. 删除所有现有表...")
            # 注意顺序：先删除关联表，再删除主表
            try:
                # 直接删除关联表
                Treet_IP_Conn.engine.execute("DROP TABLE IF EXISTS postcategories;")
                print("✓ 已删除 postcategories 表")
                
                Treet_IP_Conn.engine.execute("DROP TABLE IF EXISTS posttags;")
                print("✓ 已删除 posttags 表")
            except Exception as e:
                print(f"⚠️  删除关联表时出错: {e}")
            
            # 然后删除所有模型表
            print("正在删除所有模型表...")
            Treet_IP_Conn.drop_all()
            print("✓ 所有表已删除")
            
            # 2. 重新创建所有表
            print("\n2. 重新创建数据库表结构...")
            Treet_IP_Conn.create_all()
            print("✓ 所有表已成功创建")
            
            # 3. 验证表是否创建成功
            print("\n3. 验证表结构...")
            inspector = Treet_IP_Conn.inspect(Treet_IP_Conn.engine)
            tables = inspector.get_table_names()
        
            expected_tables = ['Users', 'Posts', 'Comments', 'Categories', 'Tags', 'postcategories', 'posttags']
        
            all_tables_exist = True
            for table in expected_tables:
                if table in tables:
                    print(f"✓ 表 '{table}' 已创建")
                else:
                    print(f"✗ 表 '{table}' 未创建")
                    all_tables_exist = False
        
            if all_tables_exist:
                print("\n✅ 数据库重置成功！所有表已重新创建。")
                print("现在可以运行 run.py 或 test_mysql_connection.py 来生成测试数据。")
            else:
                print("\n❌ 数据库重置失败！部分表未创建。")
            
    except Exception as e:
        print(f"\n❌ 数据库操作错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 操作完成 ===")