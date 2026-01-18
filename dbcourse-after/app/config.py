# 数据库配置文件
import os
import os.path

class Config:
    # 数据库配置 - 使用MySQL数据库
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost/forum_system?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 注意：在生产环境中，应该从环境变量加载SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    
    # 应用配置
    DEBUG = False  # 默认禁用调试模式以提高安全性
    
    # 缓存配置
    CACHE_TYPE = 'simple'  # 使用简单内存缓存作为默认值
    CACHE_DEFAULT_TIMEOUT = 300  # 默认缓存时间5分钟
    
    # Redis缓存配置（可选，如需使用Redis作为缓存后端）
    # CACHE_REDIS_URL = 'redis://localhost:6379/0'  # 生产环境中应从环境变量加载
    CACHE_KEY_PREFIX = 'forum_'  # 缓存键前缀
    
    # 安全配置
    SESSION_COOKIE_SECURE = False  # 在生产环境中应设置为True（需要HTTPS）
    PERMANENT_SESSION_LIFETIME = 3600  # 会话过期时间（秒）
    WTF_CSRF_ENABLED = True  # 启用CSRF保护
    
class DevelopmentConfig(Config):
    DEBUG = True  # 仅在开发环境中启用调试模式
    SQLALCHEMY_ECHO = False  # 可选：设为True查看生成的SQL语句

class ProductionConfig(Config):
    DEBUG = False
    # 生产环境安全增强配置
    SESSION_COOKIE_SECURE = True  # 启用安全Cookie（需要HTTPS）
    PREFERRED_URL_SCHEME = 'https'  # 优先使用HTTPS
    # 生产环境中推荐使用Redis或其他持久化缓存
    # CACHE_TYPE = 'redis'
    # CACHE_REDIS_URL = os.environ.get('REDIS_URL')

# 根据环境选择配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}