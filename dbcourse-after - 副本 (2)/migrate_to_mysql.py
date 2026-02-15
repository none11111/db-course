#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本
用于将项目从使用SQLite文件迁移到MySQL数据库
执行步骤：
1. 验证MySQL数据库连接
2. 创建缺失的数据库表
3. 更新表结构以匹配模型定义
4. 将项目中的SQL数据导入到MySQL数据库
5. 更新配置以使用MySQL数据库
6. 最后删除项目中的SQL文件
"""

import os
import sys
import subprocess
from app import create_app
from app.models import db
from app.utils.db_utils import create_stored_procedures, init_test_data

def check_mysql_connection():
    """检查MySQL数据库连接"""
    print("=== 步骤1：检查MySQL数据库连接 ===")
    
    app = create_app()
    with app.app_context():
        try:
            # 尝试执行一个简单的查询
            result = db.session.execute("SELECT 1").fetchone()
            if result:
                print("✓ MySQL数据库连接成功！")
                
                # 获取当前数据库名称
                db_name = db.session.execute("SELECT DATABASE()").fetchone()[0]
                print(f"✓ 当前连接的数据库: {db_name}")
                
                # 显示当前数据库连接字符串
                db_uri = app.config['SQLALCHEMY_DATABASE_URI']
                print(f"✓ 当前数据库连接字符串: {db_uri}")
                
                return True
            else:
                print("✗ MySQL数据库连接失败！")
                return False
        except Exception as e:
            print(f"✗ MySQL数据库连接错误: {e}")
            print("请检查MySQL服务是否运行以及连接配置是否正确！")
            return False

def create_missing_tables():
    """创建缺失的数据库表"""
    print("\n=== 步骤2：创建缺失的数据库表 ===")
    
    app = create_app()
    with app.app_context():
        try:
            # 只创建不存在的表
            db.create_all()
            print("✓ 数据库表结构已确保创建")
            
            # 检查所有表是否都已创建
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
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
            
            return all_tables_exist
        except Exception as e:
            print(f"✗ 创建表失败: {e}")
            return False

def update_table_structure():
    """更新表结构以匹配模型定义"""
    print("\n=== 步骤3：更新表结构 ===")
    
    # 执行MySQL表结构更新脚本
    update_script = os.path.join(os.getcwd(), 'update_mysql_schema.sql')
    if os.path.exists(update_script):
        print(f"执行表结构更新脚本: {update_script}")
        
        try:
            # 从配置中获取数据库连接信息
            app = create_app()
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            
            # 解析数据库连接字符串
            import re
            match = re.match(r'mysql\+pymysql://(.*?):(.*?)@(.*?)/(.*?)\?', db_uri)
            if match:
                username, password, host, database = match.groups()
                
                # 执行SQL脚本
                command = [
                    'mysql',
                    '-h', host,
                    '-u', username,
                    '-p' + password,  # 注意这里没有空格
                    database,
                    '-e', f'source {update_script}'
                ]
                
                # 使用subprocess执行命令
                result = subprocess.run(command, capture_output=True, text=True, shell=True)
                
                if result.returncode == 0:
                    print("✓ 表结构更新成功！")
                    return True
                else:
                    print(f"✗ 表结构更新失败: {result.stderr}")
                    return False
            else:
                print("✗ 无法解析数据库连接字符串")
                return False
        except Exception as e:
            print(f"✗ 执行更新脚本时出错: {e}")
            return False
    else:
        print(f"✗ 表结构更新脚本不存在: {update_script}")
        return False

def import_sql_data():
    """将项目中的SQL数据导入到MySQL数据库"""
    print("\n=== 步骤4：导入SQL数据 ===")
    
    # 检查是否有SQL文件需要导入
    sql_files = []
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.sql') and file not in ['update_mysql_schema.sql', 'migrate_to_mysql.py']:
                sql_files.append(os.path.join(root, file))
    
    if not sql_files:
        print("✓ 没有找到需要导入的SQL文件")
        return True
    
    print(f"找到 {len(sql_files)} 个SQL文件需要导入：")
    for sql_file in sql_files:
        print(f"  - {sql_file}")
    
    # 导入数据
    app = create_app()
    with app.app_context():
        try:
            for sql_file in sql_files:
                if os.path.exists(sql_file):
                    print(f"\n导入文件: {sql_file}")
                    
                    # 读取SQL文件内容
                    with open(sql_file, 'r', encoding='utf-8') as f:
                        sql_content = f.read()
                    
                    # 执行SQL语句（注意：这里简单处理，可能需要更复杂的SQL解析）
                    # 分割SQL语句并执行
                    sql_statements = sql_content.split(';')
                    
                    for stmt in sql_statements:
                        stmt = stmt.strip()
                        if stmt and not stmt.startswith('--') and not stmt.startswith('/*'):
                            try:
                                db.session.execute(stmt)
                            except Exception as e:
                                print(f"  ! SQL执行错误: {e}")
                                print(f"  SQL语句: {stmt}")
                                # 继续执行其他语句
                    
                    # 提交事务
                    db.session.commit()
                    print(f"  ✓ 文件导入成功")
            
            print("\n✓ 所有SQL文件导入完成！")
            return True
        except Exception as e:
            print(f"✗ 导入SQL数据时出错: {e}")
            db.session.rollback()
            return False

def update_database_config():
    """更新配置以使用MySQL数据库"""
    print("\n=== 步骤5：更新数据库配置 ===")
    
    # 检查配置文件
    config_file = os.path.join(os.getcwd(), 'app', 'config.py')
    if os.path.exists(config_file):
        print(f"检查配置文件: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # 检查是否已经使用MySQL配置
        if 'mysql+pymysql://' in config_content:
            print("✓ 配置文件已经使用MySQL数据库连接")
            return True
        else:
            print("✗ 配置文件仍使用其他数据库连接")
            print("请手动更新配置文件中的SQLALCHEMY_DATABASE_URI为MySQL连接字符串！")
            return False
    else:
        print(f"✗ 配置文件不存在: {config_file}")
        return False

def delete_sql_files():
    """删除项目中的SQL文件"""
    print("\n=== 步骤6：删除项目中的SQL文件 ===")
    
    sql_files = []
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith('.sql') and file != 'update_mysql_schema.sql':
                sql_files.append(os.path.join(root, file))
    
    if not sql_files:
        print("✓ 没有找到需要删除的SQL文件")
        return True
    
    print(f"找到 {len(sql_files)} 个SQL文件需要删除：")
    for sql_file in sql_files:
        print(f"  - {sql_file}")
    
    # 确认删除
    response = input("\n是否要删除这些SQL文件？(y/n): ")
    if response.lower() == 'y':
        deleted_count = 0
        for sql_file in sql_files:
            try:
                os.remove(sql_file)
                print(f"✓ 已删除: {sql_file}")
                deleted_count += 1
            except Exception as e:
                print(f"✗ 删除失败: {sql_file} - {e}")
        
        print(f"\n✓ 共删除了 {deleted_count} 个SQL文件")
        return True
    else:
        print("✓ 取消删除SQL文件")
        return True

def create_stored_procedures_if_needed():
    """创建必要的存储过程"""
    print("\n=== 步骤7：创建存储过程 ===")
    
    app = create_app()
    with app.app_context():
        try:
            create_stored_procedures()
            print("✓ 存储过程创建完成")
            return True
        except Exception as e:
            print(f"! 存储过程创建失败: {e}")
            print("注意：存储过程创建失败不影响应用基本功能")
            return True

def init_test_data_if_needed():
    """初始化测试数据"""
    print("\n=== 步骤8：初始化测试数据 ===")
    
    app = create_app()
    with app.app_context():
        try:
            init_test_data()
            print("✓ 测试数据初始化完成")
            return True
        except Exception as e:
            print(f"! 测试数据初始化失败: {e}")
            print("注意：测试数据初始化失败不影响应用基本功能")
            return True

def main():
    """主函数"""
    print("=" * 60)
    print("数据库迁移脚本 - SQLite到MySQL")
    print("=" * 60)
    
    # 步骤1：检查MySQL连接
    if not check_mysql_connection():
        sys.exit(1)
    
    # 步骤2：创建缺失的表
    if not create_missing_tables():
        print("\n警告：部分表创建失败，可能影响应用功能！")
    
    # 步骤3：更新表结构
    if not update_table_structure():
        print("\n警告：表结构更新失败，可能影响应用功能！")
    
    # 步骤4：导入SQL数据
    if not import_sql_data():
        print("\n警告：SQL数据导入失败，可能导致数据丢失！")
    
    # 步骤5：更新配置
    if not update_database_config():
        print("\n警告：数据库配置更新失败，应用可能仍使用旧的数据库连接！")
    
    # 步骤6：创建存储过程
    create_stored_procedures_if_needed()
    
    # 步骤7：初始化测试数据
    init_test_data_if_needed()
    
    # 步骤8：删除SQL文件（可选）
    delete_sql_files()
    
    print("\n" + "=" * 60)
    print("数据库迁移脚本执行完成！")
    print("请验证应用是否正常运行：python run.py")
    print("=" * 60)

if __name__ == '__main__':
    main()