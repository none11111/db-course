#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的数据库连接测试脚本
用于验证与现有数据库的连接，不创建任何表
"""

from app import create_app
from app.models import db

# 创建应用实例
app = create_app()

with app.app_context():
    print("=== 简单数据库连接测试 ===")
    
    try:
        # 1. 检查数据库连接
        print("\n1. 检查数据库连接...")
        result = db.session.execute("SELECT 1").fetchone()
        if result:
            print("✓ 数据库连接成功！")
        else:
            print("✗ 数据库连接失败！")
            exit(1)
        
        # 2. 检查数据库名称
        print("\n2. 检查当前数据库...")
        db_name = db.session.execute("SELECT DATABASE()").fetchone()[0]
        print(f"✓ 当前连接的数据库: {db_name}")
        
        # 3. 检查数据库表
        print("\n3. 检查数据库表...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        # 转换为小写进行比较，因为数据库表名可能是小写的
        tables_lower = [table.lower() for table in tables]
        
        expected_tables = ['users', 'posts', 'comments', 'categories', 'tags', 'postcategories', 'posttags']
        
        all_tables_exist = True
        for table in expected_tables:
            if table in tables_lower:
                actual_table_name = tables[tables_lower.index(table)]
                print(f"✓ 表 '{actual_table_name}' 存在")
            else:
                print(f"✗ 表 '{table}' 不存在")
                all_tables_exist = False
        
        # 4. 检查配置文件中的数据库连接
        print("\n4. 检查配置信息...")
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"✓ 当前数据库连接字符串: {db_uri}")
        
        # 5. 查询categories表内容
        print("\n5. 查询categories表内容...")
        try:
            # 检查表名是否存在（可能是大小写问题）
            categories_table_name = None
            for table in tables:
                if table.lower() == 'categories':
                    categories_table_name = table
                    break
            
            if categories_table_name:
                # 查询categories表内容
                categories = db.session.execute(f"SELECT * FROM {categories_table_name}").fetchall()
                if categories:
                    print(f"✓ 表 '{categories_table_name}' 包含 {len(categories)} 条记录")
                    print("记录内容:")
                    for cat in categories:
                        print(f"  - {cat}")
                else:
                    print(f"⚠️  表 '{categories_table_name}' 当前为空")
                    print("这是一个分类表，用于存储论坛帖子的分类信息")
            else:
                print("✗ 未找到categories表")
        except Exception as e:
            print(f"❌ 查询categories表失败: {e}")

        if all_tables_exist:
            print("\n✅ 所有测试通过！")
            print("您的项目已成功连接到现有数据库 'forum_system'")
            print("现在可以直接运行应用: python run.py")
        else:
            print("\n⚠️  部分表不存在")
            print("但连接到数据库 'forum_system' 成功")
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试完成 ===")