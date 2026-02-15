from flask import Flask
from flask_login import LoginManager
from flask_caching import Cache
from .config import config
from .models import Treet_IP_Conn
import os

# 创建缓存实例
cache = Cache()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')
    
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化数据库
    Treet_IP_Conn.init_app(app)
    
    # 初始化缓存
    cache.init_app(app)
    
    # 初始化Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # 设置登录视图
    login_manager.login_message = '请先登录以访问该页面'
    login_manager.login_message_category = 'info'
    
    # 注册自定义过滤器
    from .filters import level_name
    app.jinja_env.filters['level_name'] = level_name
    
    @login_manager.user_loader
    def load_user(user_id):
        """用户加载器"""
        from .models import User
        return User.query.get(int(user_id))
    
    # 注册蓝图
    from .routes.views import main as main_blueprint
    from .routes.auth import auth as auth_blueprint
    from .routes.forum import forum as forum_blueprint
    from .routes.points import points as points_blueprint
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(forum_blueprint, url_prefix='/forum')
    app.register_blueprint(points_blueprint, url_prefix='/points')
    
    # 创建数据库表（开发环境下）
    with app.app_context():
        try:
            Treet_IP_Conn.create_all()
            print("数据库表创建成功")
        except Exception as e:
            print(f"数据库表创建失败: {e}")
    
    return app