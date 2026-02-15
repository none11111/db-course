from . import Treet_IP_Conn
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import enum

class UserRole(enum.Enum):
    """用户角色枚举"""
    ADMIN = 'ADMIN'
    USER = 'USER'

class UserStatus(enum.Enum):
    """用户状态枚举"""
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    BANNED = 'BANNED'

class User(UserMixin, Treet_IP_Conn.Model):
    __tablename__ = 'users'
    
    # 主键
    UserID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, primary_key=True, autoincrement=True)
    
    # 用户基本信息 - 与SQL脚本保持一致
    UserName = Treet_IP_Conn.Column(Treet_IP_Conn.String(50), unique=True, nullable=False, index=True)
    UserEmail = Treet_IP_Conn.Column(Treet_IP_Conn.String(100), unique=True, nullable=True, index=True)
    RegistrationDate = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, default=datetime.utcnow, index=True)  # 添加索引以优化按注册时间查询
    LastLoginTime = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)  # 添加索引以优化按登录时间查询
    PasswordHash = Treet_IP_Conn.Column(Treet_IP_Conn.String(255), nullable=False)
    Reputation = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, default=0, index=True)  # 用户声望值
    Status = Treet_IP_Conn.Column(Treet_IP_Conn.Enum(UserStatus), default=UserStatus.ACTIVE, index=True)  # 添加索引以优化状态筛选
    Role = Treet_IP_Conn.Column(Treet_IP_Conn.Enum(UserRole), default=UserRole.USER, index=True)  # 添加用户角色
    UserBio = Treet_IP_Conn.Column(Treet_IP_Conn.Text, default='')  # 个人简介
    AvatarURL = Treet_IP_Conn.Column(Treet_IP_Conn.String(255), default='')  # 头像URL
    
    # 关系定义
    posts = Treet_IP_Conn.relationship('Post', backref='author', foreign_keys='Post.UserID', lazy='dynamic', cascade='all, delete-orphan')
    comments = Treet_IP_Conn.relationship('Comment', backref='author', foreign_keys='Comment.UserID', lazy='dynamic', cascade='all, delete-orphan')
    
    # Flask-Login 必需的方法
    def get_id(self):
        """Flask-Login 必需的方法，返回用户唯一标识符"""
        return str(self.UserID)
    
    # 确保用户模型有正确的属性名映射
    @property
    def id(self):
        """为Flask-Login提供id属性（兼容常见使用方式）"""
        return self.UserID
    
    def is_active(self):
        return self.Status == UserStatus.ACTIVE
    
    # 权限检查方法
    def can_post(self):
        """检查用户是否可以发帖"""
        return self.is_active() and self.Status != UserStatus.BANNED
    
    def can_comment(self):
        """检查用户是否可以评论"""
        return self.is_active() and self.Status != UserStatus.BANNED
    
    def is_admin(self):
        """检查用户是否是管理员"""
        return self.Role == UserRole.ADMIN
    
    def can_delete_post(self, post):
        """检查用户是否可以删除帖子"""
        return self.is_admin() or self.UserID == post.UserID
    
    def can_approve_post(self, post):
        """检查用户是否可以审核帖子"""
        return self.is_admin()
    
    def can_sticky_post(self, post):
        """检查用户是否可以置顶帖子"""
        return self.is_admin()
    
    def can_delete_comment(self, comment):
        """检查用户是否可以删除评论
        管理员可以删除所有评论，普通用户只能删除自己的评论
        """
        return self.is_admin() or comment.UserID == self.UserID
    
    # 设置密码（加密）
    def set_password(self, password):
        """设置用户密码（加密）"""
        self.PasswordHash = generate_password_hash(password)
    
    # 验证密码
    def check_password(self, password):
        """验证用户密码"""
        return check_password_hash(self.PasswordHash, password)
    
    # 更新声望值
    def update_reputation(self, amount):
        """更新用户声望值"""
        self.Reputation = max(0, self.Reputation + amount)  # 声望值不能为负
    
    # 生成JWT令牌
    def generate_token(self, expiration=3600):
        """生成JWT令牌"""
        import jwt
        from flask import current_app
        return jwt.encode(
            {'user_id': self.UserID, 'exp': datetime.utcnow().timestamp() + expiration},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_token(token):
        """验证JWT令牌"""
        import jwt
        from flask import current_app
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return User.query.get(data['user_id'])
        except:
            return None
    
    def __repr__(self):
        return f'<User {self.UserName}>'