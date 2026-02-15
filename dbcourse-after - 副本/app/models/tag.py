from . import Treet_IP_Conn

class Tag(Treet_IP_Conn.Model):
    __tablename__ = 'tags'
    
    # 主键
    TagID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, primary_key=True, autoincrement=True)
    
    # 标签信息 - 与SQL脚本保持一致
    TagName = Treet_IP_Conn.Column(Treet_IP_Conn.String(50), nullable=False, unique=True, index=True)
    UsageCount = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, default=0)
    
    def __repr__(self):
        return f'<Tag {self.TagName}>'