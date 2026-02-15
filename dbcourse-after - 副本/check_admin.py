from app import create_app, Treet_IP_Conn
from app.models.user import User, UserRole, UserStatus
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # 查询所有用户及其角色
    users = User.query.all()
    print(f"数据库中共有 {len(users)} 个用户：")
    for user in users:
        print(f"  - ID: {user.UserID}, 用户名: {user.UserName}, 角色: {user.Role.value}")

    # 检查是否有管理员
    admin_users = User.query.filter_by(Role=UserRole.ADMIN).all()
    print(f"\n管理员用户数量: {len(admin_users)}")

    if not admin_users:
        print("\n没有找到管理员用户，正在创建管理员账号...")
        # 创建管理员账号
        admin = User(
            UserName='admin',
            UserEmail='admin@example.com',
            Role=UserRole.ADMIN,
            Status=UserStatus.ACTIVE
        )
        admin.PasswordHash = generate_password_hash('admin123')
        Treet_IP_Conn.session.add(admin)
        Treet_IP_Conn.session.commit()
        print("✓ 管理员账号创建成功！")
        print("  用户名: admin")
        print("  密码: admin123")
        print("  邮箱: admin@example.com")
    else:
        print("\n管理员用户列表：")
        for admin in admin_users:
            print(f"  - {admin.UserName} (ID: {admin.UserID})")
