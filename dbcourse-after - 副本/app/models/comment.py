from . import Treet_IP_Conn
from datetime import datetime

class Comment(Treet_IP_Conn.Model):
    __tablename__ = 'comments'
    
    # 主键
    CommentID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, primary_key=True, autoincrement=True)
    
    # 评论内容 - 与SQL脚本保持一致
    CommentContent = Treet_IP_Conn.Column(Treet_IP_Conn.Text, nullable=False)
    CreationTime = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, default=datetime.utcnow, index=True)
    LikeCount = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, default=0, index=True)  # 添加索引以优化热门评论查询
    Status = Treet_IP_Conn.Column(Treet_IP_Conn.String(10), default='approved', index=True)
    
    # AI审核信息
    AIAuditResult = Treet_IP_Conn.Column(Treet_IP_Conn.Boolean, nullable=True, index=True)  # AI审核结果：True表示合规，False表示违规
    AIAuditTime = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, nullable=True, index=True)  # AI审核时间
    IsAIAudit = Treet_IP_Conn.Column(Treet_IP_Conn.Boolean, default=False, index=True)  # 是否由AI进行审核
    
    # 人工审核信息
    AuditUserID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('users.UserID', ondelete='SET NULL'), nullable=True, index=True)
    AuditTime = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, nullable=True, index=True)
    ReviewComment = Treet_IP_Conn.Column(Treet_IP_Conn.Text, nullable=True)
    
    # 外键关联 - 与SQL脚本保持一致
    UserID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('users.UserID', ondelete='CASCADE'), nullable=False, index=True)
    PostID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('posts.PostID', ondelete='CASCADE'), nullable=False, index=True)
    
    # 自关联（用于回复功能）- 与SQL脚本保持一致
    ParentCommentID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('comments.CommentID', ondelete='CASCADE'), nullable=True, index=True)
    
    # 关系定义 - author和post关系分别由User和Post模型定义
    replies = Treet_IP_Conn.relationship(
        'Comment',
        backref=Treet_IP_Conn.backref('parent', remote_side=[CommentID]),
        lazy='select',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        return f'<Comment {self.CommentID}>'