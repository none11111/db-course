#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询categories表内容的脚本
"""

from app import create_app
from app.models import db

# 创建应用实例
app = create_app()

with app.app_context():
    print("=== 查询categories表内容 ===")
    
    try:
        # 查询categories表内容
        # 先检查数据库引擎
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        # 查找categories表（可能是大小写问题）
        categories_table_name = None
        for table in tables:
            if table.lower() == 'categories':
                categories_table_name = table
                break
        
        if categories_table_name:
            print(f"找到表: {categories_table_name}")
            
            # 查询表结构
            print("\n表结构:")
            columns = inspector.get_columns(categories_table_name)
            for column in columns:
                print(f"- {column['name']} ({column['type']})")
            
            # 查询表内容
            print("\n表内容:")
            categories = db.session.execute(f"SELECT * FROM {categories_table_name}").fetchall()
            
            if categories:
                print(f"✓ 表包含 {len(categories)} 条记录")
                print("记录:")
                for cat in categories:
                    print(f"  - {cat}")
            else:
                print("⚠️  表当前为空")
                print("\n结论:")
                print("这是一个分类表(Categories)，用于存储论坛帖子的分类信息")
                print("它确实是您所说的'类型表'，目前为空是因为您还没有添加任何分类")
        else:
            print("❌ 未找到categories表")
            print("可用表:", tables)
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 查询完成 ===")