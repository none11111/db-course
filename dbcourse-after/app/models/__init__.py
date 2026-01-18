from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 创建数据库实例
Treet_IP_Conn = SQLAlchemy()

# 导入所有模型
from .user import User, UserStatus, UserRole
from .post import Post
from .comment import Comment
from .category import Category
from .tag import Tag