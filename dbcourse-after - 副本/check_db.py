from app import create_app
from app.models import db, User

# 创建应用实例
app = create_app()

with app.app_context():
    print("=== 数据库表结构检查 ===")
    
    # 打印所有表名
    print("\n数据库中的所有表:")
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    for table in tables:
        print(f"- {table}")
    
    # 检查users表是否存在
    if 'users' in tables:
        print("\nusers表存在！")
        
        # 获取表结构
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = inspector.get_columns('users')
        
        print("\nusers表的列:")
        for column in columns:
            print(f"- {column['name']} ({column['type']})")
        
        # 尝试查询用户
        print("\n当前用户数量:", User.query.count())
        
        # 测试添加一个临时用户
        try:
            print("\n测试添加临时用户...")
            test_user = User(UserName='test_user_db', UserEmail='test_db@example.com')
            test_user.set_password('test123')
            db.session.add(test_user)
            db.session.commit()
            print(f"成功添加临时用户，ID: {test_user.UserID}")
            
            # 验证用户是否存在
            found_user = User.query.filter_by(UserName='test_user_db').first()
            if found_user:
                print(f"验证成功: 找到用户 '{found_user.UserName}'")
            else:
                print("验证失败: 未找到刚添加的用户")
            
            # 清理测试数据
            db.session.delete(test_user)
            db.session.commit()
            print("清理临时用户数据完成")
            
        except Exception as e:
            print(f"添加测试用户时出错: {e}")
            db.session.rollback()
    else:
        print("\n错误: users表不存在！")
        print("尝试重新创建数据库表...")
        try:
            db.create_all()
            print("数据库表创建成功")
        except Exception as e:
            print(f"创建数据库表失败: {e}")
    
    print("\n=== 检查完成 ===")