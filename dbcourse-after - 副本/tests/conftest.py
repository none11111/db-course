import pytest
import os
import tempfile
from app import create_app
from app.models import Treet_IP_Conn, User, Post, Comment

@pytest.fixture
def app():
    """创建并配置一个新的应用实例用于每次测试"""
    # 创建临时数据库文件
    db_fd, db_path = tempfile.mkstemp(suffix='.sqlite')
    
    # 创建应用，使用测试配置
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:123456@localhost/forum_system_test?charset=utf8mb4',
        'WTF_CSRF_ENABLED': False,  # 测试时禁用CSRF保护
        'DEBUG': False
    })
    
    # 创建数据库表
    with app.app_context():
        Treet_IP_Conn.create_all()
        
        # 创建一些测试数据
        user1 = User(UserName='testuser1', UserEmail='test1@example.com')
        user1.set_password('test123')
        user2 = User(UserName='testuser2', UserEmail='test2@example.com')
        user2.set_password('test123')
        Treet_IP_Conn.session.add_all([user1, user2])
        Treet_IP_Conn.session.commit()
        
        post1 = Post(PostTitle='测试帖子1', PostContent='这是第一个测试帖子', UserID=user1.UserID)
        post2 = Post(PostTitle='测试帖子2', PostContent='这是第二个测试帖子', UserID=user2.UserID)
        Treet_IP_Conn.session.add_all([post1, post2])
        Treet_IP_Conn.session.commit()
        
        comment1 = Comment(CommentContent='这是第一条评论', PostID=post1.PostID, UserID=user2.UserID)
        Treet_IP_Conn.session.add(comment1)
        Treet_IP_Conn.session.commit()
    
    yield app
    
    # 清理临时数据库
    with app.app_context():
        Treet_IP_Conn.session.remove()
        Treet_IP_Conn.drop_all()
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """创建一个测试客户端"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """创建一个测试CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    """创建一个认证辅助类，用于模拟登录"""
    class AuthActions:
        def login(self, username='testuser1', password='test123'):
            return client.post('/login', data={
                'username': username,
                'password': password
            }, follow_redirects=True)
        
        def logout(self):
            return client.get('/logout', follow_redirects=True)
    
    return AuthActions()