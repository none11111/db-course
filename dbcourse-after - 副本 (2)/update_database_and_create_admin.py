from app import create_app
from app.models import db, User, UserStatus, UserRole
from werkzeug.security import generate_password_hash
from datetime import datetime

# 创建Flask应用实例
app = create_app()

with app.app_context():
    # 更新数据库结构
    print("正在更新数据库结构...")
    
    # 连接到数据库
    connection = db.engine.raw_connection()
    cursor = connection.cursor()
    
    try:
        # 为Users表添加缺失的字段
        # 检查Role字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'Role'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN Role ENUM('admin', 'user') DEFAULT 'user' NOT NULL")
            print("✓ 添加了Role字段")
        
        # 检查UserEmail字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'UserEmail'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN UserEmail VARCHAR(100) NULL DEFAULT NULL")
            print("✓ 添加了UserEmail字段")
        
        # 检查LastLoginTime字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'LastLoginTime'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN LastLoginTime DATETIME NULL DEFAULT NULL")
            print("✓ 添加了LastLoginTime字段")
        
        # 检查Reputation字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'Reputation'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN Reputation INT DEFAULT 0 NOT NULL")
            print("✓ 添加了Reputation字段")
        
        # 检查Status字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'Status'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN Status ENUM('active', 'inactive', 'banned') DEFAULT 'active' NOT NULL")
            print("✓ 添加了Status字段")
        
        # 检查UserBio字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'UserBio'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN UserBio TEXT DEFAULT ''")
            print("✓ 添加了UserBio字段")
        
        # 检查AvatarURL字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'AvatarURL'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN AvatarURL VARCHAR(255) DEFAULT ''")
            print("✓ 添加了AvatarURL字段")
        
        # 检查RegistrationDate字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'RegistrationDate'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL")
            print("✓ 添加了RegistrationDate字段")
        
        # 提交更改
        connection.commit()
        print("数据库结构更新完成！")
        
    except Exception as e:
        print(f"更新数据库结构时出错: {str(e)}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
    
    print("\n正在创建root管理员账号...")
    
    try:
        # 检查是否已经存在root用户
        root_user = User.query.filter_by(UserName='root').first()
        
        if root_user:
            print("root用户已经存在")
        else:
            # 创建root用户
            root_user = User(
                UserName='root',
                UserEmail='root@example.com',
                PasswordHash=generate_password_hash('123456'),
                Role=UserRole.ADMIN,
                Status=UserStatus.ACTIVE,
                RegistrationDate=datetime.utcnow(),
                LastLoginTime=datetime.utcnow()
            )
            
            # 添加到数据库
            db.session.add(root_user)
            db.session.commit()
            
            print("root管理员账号创建成功！")
            print(f"用户名: {root_user.UserName}")
            print(f"角色: {root_user.Role}")
            print(f"状态: {root_user.Status}")
    except Exception as e:
        print(f"创建root管理员账号时出错: {str(e)}")
        db.session.rollback()
from app import create_app
from app.models import db, User, UserStatus, UserRole
from werkzeug.security import generate_password_hash
from datetime import datetime

# 创建Flask应用实例
app = create_app()

with app.app_context():
    # 更新数据库结构
    print("正在更新数据库结构...")
    
    # 连接到数据库
    connection = db.engine.raw_connection()
    cursor = connection.cursor()
    
    try:
        # 为Users表添加缺失的字段
        # 检查Role字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'Role'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN Role ENUM('admin', 'user') DEFAULT 'user' NOT NULL")
            print("✓ 添加了Role字段")
        
        # 检查UserEmail字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'UserEmail'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN UserEmail VARCHAR(100) NULL DEFAULT NULL")
            print("✓ 添加了UserEmail字段")
        
        # 检查LastLoginTime字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'LastLoginTime'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN LastLoginTime DATETIME NULL DEFAULT NULL")
            print("✓ 添加了LastLoginTime字段")
        
        # 检查Reputation字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'Reputation'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN Reputation INT DEFAULT 0 NOT NULL")
            print("✓ 添加了Reputation字段")
        
        # 检查Status字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'Status'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN Status ENUM('active', 'inactive', 'banned') DEFAULT 'active' NOT NULL")
            print("✓ 添加了Status字段")
        
        # 检查UserBio字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'UserBio'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN UserBio TEXT DEFAULT ''")
            print("✓ 添加了UserBio字段")
        
        # 检查AvatarURL字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'AvatarURL'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN AvatarURL VARCHAR(255) DEFAULT ''")
            print("✓ 添加了AvatarURL字段")
        
        # 检查RegistrationDate字段是否存在
        cursor.execute("SHOW COLUMNS FROM Users LIKE 'RegistrationDate'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE Users ADD COLUMN RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL")
            print("✓ 添加了RegistrationDate字段")
        
        # 提交更改
        connection.commit()
        print("数据库结构更新完成！")
        
    except Exception as e:
        print(f"更新数据库结构时出错: {str(e)}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
    
    print("\n正在创建root管理员账号...")
    
    try:
        # 检查是否已经存在root用户
        root_user = User.query.filter_by(UserName='root').first()
        
        if root_user:
            print("root用户已经存在")
        else:
            # 创建root用户
            root_user = User(
                UserName='root',
                UserEmail='root@example.com',
                PasswordHash=generate_password_hash('123456'),
                Role=UserRole.ADMIN,
                Status=UserStatus.ACTIVE,
                RegistrationDate=datetime.utcnow(),
                LastLoginTime=datetime.utcnow()
            )
            
            # 添加到数据库
            db.session.add(root_user)
            db.session.commit()
            
            print("root管理员账号创建成功！")
            print(f"用户名: {root_user.UserName}")
            print(f"角色: {root_user.Role}")
            print(f"状态: {root_user.Status}")
    except Exception as e:
        print(f"创建root管理员账号时出错: {str(e)}")
        db.session.rollback()