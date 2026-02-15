from app.models import Treet_IP_Conn, User, Post, Comment, UserStatus
import pytest

class TestUserModel:
    def test_password_setter(self):
        """测试密码设置功能"""
        u = User(username='test', email='test@example.com')
        u.set_password('test_password')
        assert u.password_hash is not None
    
    def test_password_verification(self):
        """测试密码验证功能"""
        u = User(username='test', email='test@example.com')
        u.set_password('test_password')
        assert u.check_password('test_password') is True
        assert u.check_password('wrong_password') is False
    
    def test_user_creation(self):
        """测试用户创建和基本属性"""
        u = User(username='newtest', email='new@example.com')
        u.set_password('test123')
        Treet_IP_Conn.session.add(u)
        Treet_IP_Conn.session.commit()
        
        # 验证用户是否正确创建
        assert u.id is not None
        assert u.username == 'newtest'
        assert u.email == 'new@example.com'
        assert u.status == UserStatus.ACTIVE

class TestPostModel:
    def test_post_creation(self, app):
        """测试帖子创建功能"""
        with app.app_context():
            user = User.query.filter_by(username='testuser1').first()
            post = Post(title='新测试帖子', content='这是测试内容', author_id=user.id)
            Treet_IP_Conn.session.add(post)
            Treet_IP_Conn.session.commit()
            
            assert post.PostID is not None
            assert post.title == '新测试帖子'
            assert post.author.username == 'testuser1'
    
    def test_post_update(self, app):
        """测试帖子更新功能"""
        with app.app_context():
            post = Post.query.filter_by(title='测试帖子1').first()
            old_content = post.content
            post.update_content('更新后的内容')
            Treet_IP_Conn.session.commit()
            
            updated_post = Post.query.get(post.PostID)
            assert updated_post.content != old_content
            assert updated_post.content == '更新后的内容'

class TestCommentModel:
    def test_comment_creation(self, app):
        """测试评论创建功能"""
        with app.app_context():
            user = User.query.filter_by(username='testuser1').first()
            post = Post.query.filter_by(title='测试帖子2').first()
            
            comment = Comment(content='这是测试评论', PostID=post.PostID, UserID=user.UserID)
            Treet_IP_Conn.session.add(comment)
            Treet_IP_Conn.session.commit()
            
            assert comment.id is not None
            assert comment.content == '这是测试评论'
            assert comment.user.username == 'testuser1'
            assert comment.post.title == '测试帖子2'