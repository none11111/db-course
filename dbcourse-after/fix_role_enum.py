from app import create_app
from app.models import db, User, UserRole, UserStatus
from werkzeug.security import generate_password_hash
from datetime import datetime

# 创建Flask应用实例
app = create_app()

with app.app_context():
    # 连接到数据库
    connection = db.engine.raw_connection()
    cursor = connection.cursor()
    
    try:
        # 检查并修复Role字段的枚举定义
        print("检查并修复Role字段的枚举定义...")
        
        # 查看当前的枚举定义
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'Role'")
        role_column = cursor.fetchone()
        print(f"当前Role字段定义: {role_column}")
        
        # 修改枚举定义，使用正确的值
        cursor.execute("ALTER TABLE Users MODIFY COLUMN Role ENUM('ADMIN', 'USER') DEFAULT 'USER' NOT NULL")
        print("已修复Role字段的枚举定义")
        
        # 如果root用户不存在，创建它
        print("\n检查root用户...")
        root_user = User.query.filter_by(UserName='root').first()
        
        if root_user:
            print("root用户已存在，更新其角色为admin")
            root_user.Role = UserRole.ADMIN
            db.session.commit()
        else:
            print("创建root用户...")
            root_user = User(
                UserName='root',
                UserEmail='root@example.com',
                PasswordHash=generate_password_hash('123456'),
                Role=UserRole.ADMIN,
                Status=UserStatus.ACTIVE,
                RegistrationDate=datetime.utcnow(),
                LastLoginTime=datetime.utcnow()
            )
            db.session.add(root_user)
            db.session.commit()
            print("root用户创建成功")
        
        # 提交所有更改
        connection.commit()
        print("\n修复完成！")
        
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        connection.rollback()
        db.session.rollback()
    finally:
        cursor.close()
        connection.close()