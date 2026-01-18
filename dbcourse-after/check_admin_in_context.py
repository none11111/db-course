from app import create_app
from app.models import Treet_IP_Conn, User
from app.models.user import UserRole, UserStatus

# 创建Flask应用实例
app = create_app()

# 在应用上下文中执行查询
with app.app_context():
    # 查询所有管理员账号
    admin_users = User.query.filter_by(Role=UserRole.ADMIN).all()
    print(f"找到 {len(admin_users)} 个管理员账号:")
    
    for admin in admin_users:
        print(f"\n用户名: {admin.UserName}")
        print(f"用户ID: {admin.UserID}")
        print(f"角色: {admin.Role}")
        print(f"状态: {admin.Status}")
        print(f"密码哈希: {admin.PasswordHash}")
        print(f"注册时间: {admin.RegistrationDate}")
        print(f"最后登录时间: {admin.LastLoginTime}")
    
    # 也查询所有用户，查看是否有异常
    all_users = User.query.all()
    print(f"\n\n所有用户 ({len(all_users)} 个):")
    for user in all_users:
        print(f"用户名: {user.UserName}, 角色: {user.Role}, 状态: {user.Status}")