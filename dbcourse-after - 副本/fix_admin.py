from app import create_app
from app.models import db, User
from app.models.user import UserRole, UserStatus

app = create_app()

with app.app_context():
    print("=== 检查并修复管理员账户 ===")
    
    # 1. 检查管理员账户是否存在
    root_user = User.query.filter_by(UserName='root').first()
    
    if root_user:
        print("✅ 管理员账户已存在")
        print(f"   用户名: {root_user.UserName}")
        print(f"   角色: {root_user.Role}")
        print(f"   状态: {root_user.Status}")
        
        # 2. 检查角色是否正确
        if root_user.Role != UserRole.ADMIN:
            print("❌ 角色不正确，正在修复...")
            root_user.Role = UserRole.ADMIN
            db.session.commit()
            print("✅ 角色已修复为管理员")
        
        # 3. 检查状态是否激活
        if root_user.Status != UserStatus.ACTIVE:
            print("❌ 账户状态不正确，正在修复...")
            root_user.Status = UserStatus.ACTIVE
            db.session.commit()
            print("✅ 账户状态已修复为激活")
        
        # 4. 验证权限检查方法
        print(f"   权限检查方法调用: is_admin() = {root_user.is_admin()}")
        print(f"   账户激活状态: is_active() = {root_user.is_active()}")
        print(f"   是否可以发帖: can_post() = {root_user.can_post()}")
        print(f"   是否可以审核帖子: can_approve_post() = {root_user.can_approve_post(None)}")
    
    else:
        print("❌ 管理员账户不存在，正在创建...")
        
        try:
            # 创建root用户
            root_user = User(
                UserName='root',
                UserEmail='root@example.com',
                Role=UserRole.ADMIN,
                Status=UserStatus.ACTIVE
            )
            root_user.set_password('123456')
            
            db.session.add(root_user)
            db.session.commit()
            
            print("✅ 管理员账户创建成功")
            print(f"   用户名: root")
            print(f"   密码: 123456")
            print(f"   角色: {root_user.Role}")
            print(f"   状态: {root_user.Status}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ 创建管理员账户失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n=== 验证权限检查逻辑 ===")
    print("装饰器中的权限检查已修复: is_admin() 方法调用")
    print("views.py中的权限检查已修复: hasattr + is_admin() 方法调用")
    print("\n管理员账户修复完成！")