from . import Treet_IP_Conn
from datetime import datetime

# 多对多关联表：Post和Category - 与SQL脚本保持一致
postcategories = Treet_IP_Conn.Table('postcategories',
    Treet_IP_Conn.Column('PostID', Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('posts.PostID'), primary_key=True),
    Treet_IP_Conn.Column('CategoryID', Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('categories.CategoryID'), primary_key=True)
)

# 多对多关联表：Post和Tag - 与SQL脚本保持一致
posttags = Treet_IP_Conn.Table('posttags',
    Treet_IP_Conn.Column('PostID', Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('posts.PostID'), primary_key=True),
    Treet_IP_Conn.Column('TagID', Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('tags.TagID'), primary_key=True)
)

class Post(Treet_IP_Conn.Model):
    __tablename__ = 'posts'
    
    # 帖子状态常量
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    
    # 主键
    PostID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, primary_key=True, autoincrement=True)
    
    # 帖子内容 - 与SQL脚本保持一致
    PostTitle = Treet_IP_Conn.Column(Treet_IP_Conn.String(200), nullable=False, index=True)  # 添加索引以优化标题搜索
    PostContent = Treet_IP_Conn.Column(Treet_IP_Conn.Text, nullable=False)
    
    # 时间戳
    PublishTime = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, nullable=True, index=True)  # 添加索引以优化发布时间查询
    LastModified = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)  # 添加索引以优化修改时间查询
    CreationTime = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, default=datetime.utcnow, index=True)
    
    # 状态和统计
    Status = Treet_IP_Conn.Column(Treet_IP_Conn.String(20), default=STATUS_PENDING, index=True)  # pending, approved, rejected
    ViewCount = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, default=0, index=True)
    IsSticky = Treet_IP_Conn.Column(Treet_IP_Conn.Boolean, default=False, index=True)  # 是否置顶
    
    # 审核信息
    ReviewerID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('users.UserID', ondelete='SET NULL'), nullable=True, index=True)
    ReviewTime = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, nullable=True, index=True)
    ReviewComment = Treet_IP_Conn.Column(Treet_IP_Conn.Text, nullable=True)
    
    # AI审核信息
    AIAuditResult = Treet_IP_Conn.Column(Treet_IP_Conn.Boolean, nullable=True, index=True)  # AI审核结果：True表示合规，False表示违规
    AIAuditTime = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, nullable=True, index=True)  # AI审核时间
    IsAIAudit = Treet_IP_Conn.Column(Treet_IP_Conn.Boolean, default=False, index=True)  # 是否由AI进行审核
    
    # 外键关联 - 与SQL脚本保持一致
    UserID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('users.UserID', ondelete='CASCADE'), nullable=False, index=True)
    
    # 审核员关系
    reviewer = Treet_IP_Conn.relationship('User', foreign_keys=[ReviewerID], backref='reviewed_posts')
    
    # 关系定义 - author关系由User模型定义
    comments = Treet_IP_Conn.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    # 与Category的多对多关系
    categories = Treet_IP_Conn.relationship('Category', secondary='postcategories', backref=Treet_IP_Conn.backref('posts', lazy='dynamic'))
    # 与Tag的多对多关系
    tags = Treet_IP_Conn.relationship('Tag', secondary=posttags, backref=Treet_IP_Conn.backref('posts', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Post {self.PostTitle}>'
    
    # 审核相关方法
    def approve(self, reviewer):
        """批准帖子"""
        self.Status = 'approved'
        self.ReviewerID = reviewer.UserID
        self.ReviewComment = None
        self.ReviewTime = datetime.utcnow()
        self.IsAIAudit = False  # 标记为人工审核

    def reject(self, reviewer, comment):
        """拒绝帖子"""
        self.Status = 'rejected'
        self.ReviewerID = reviewer.UserID
        self.ReviewComment = comment
        self.ReviewTime = datetime.utcnow()
        self.IsAIAudit = False  # 标记为人工审核

    def resubmit(self):
        """重新提交帖子"""
        self.Status = 'pending'
        self.ReviewerID = None
        self.ReviewComment = None
        self.ReviewTime = None

    def toggle_sticky(self):
        """切换置顶状态"""
        self.IsSticky = not self.IsSticky