import pytest
from flask import json

class TestBasicRoutes:
    def test_index_page(self, client):
        """测试首页访问"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<title>论坛首页</title>' in response.data
    
    def test_login_page(self, client):
        """测试登录页面访问"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'<title>登录</title>' in response.data
    
    def test_registration_page(self, client):
        """测试注册页面访问"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'<title>注册</title>' in response.data

class TestAuthRoutes:
    def test_registration(self, client, app):
        """测试用户注册功能"""
        # 发送注册请求
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'password2': 'newpassword'
        }, follow_redirects=True)
        
        # 验证注册是否成功
        assert response.status_code == 200
        assert b'注册成功' in response.data or b'登录' in response.data
        
    def test_login(self, client, auth):
        """测试用户登录功能"""
        response = auth.login()
        assert response.status_code == 200
        assert b'登录成功' in response.data or b'退出' in response.data
        
    def test_logout(self, client, auth):
        """测试用户登出功能"""
        auth.login()  # 先登录
        response = auth.logout()
        assert response.status_code == 200
        assert b'登录' in response.data

class TestAPIRoutes:
    def test_api_overview_stats(self, client):
        """测试/api/stats/overview接口"""
        response = client.get('/api/stats/overview')
        assert response.status_code == 200
        
        # 验证返回的数据格式
        data = json.loads(response.data)
        assert isinstance(data, dict)
        assert 'total_users' in data
        assert 'total_posts' in data
        assert 'total_comments' in data
        assert isinstance(data['total_users'], int)
        assert isinstance(data['total_posts'], int)
        assert isinstance(data['total_comments'], int)
    
    def test_api_posts(self, client):
        """测试/api/posts接口"""
        response = client.get('/api/posts')
        assert response.status_code == 200
        
        # 验证返回的数据格式
        data = json.loads(response.data)
        assert isinstance(data, list)
        if data:  # 如果有数据
            assert 'id' in data[0]
            assert 'title' in data[0]
            assert 'content' in data[0]
    
    def test_api_get_user(self, client):
        """测试/api/user/<id>接口"""
        response = client.get('/api/user/1')
        assert response.status_code == 200 or response.status_code == 404
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, dict)
            assert 'username' in data
            assert 'email' in data