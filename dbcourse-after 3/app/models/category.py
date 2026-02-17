from . import Treet_IP_Conn

class Category(Treet_IP_Conn.Model):
    __tablename__ = 'categories'
    
    # 主键
    CategoryID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, primary_key=True, autoincrement=True)
    
    # 分类信息 - 与SQL脚本保持一致
    CategoryName = Treet_IP_Conn.Column(Treet_IP_Conn.String(50), nullable=False, unique=True, index=True)
    Description = Treet_IP_Conn.Column(Treet_IP_Conn.String(200))
    IsActive = Treet_IP_Conn.Column(Treet_IP_Conn.Boolean, default=True)
    
    # 关系定义已在Post模型中通过category属性定义
    
    def __repr__(self):
        return f'<Category {self.CategoryName}>'