from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.models.user import UserStatus

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'info')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('您没有管理员权限访问此页面', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """普通用户权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'info')
            return redirect(url_for('auth.login'))
        
        # 检查用户状态
        if current_user.Status == UserStatus.BANNED:
            flash('您的账号已被封禁', 'danger')
            return redirect(url_for('auth.login'))
            
        if current_user.Status == UserStatus.INACTIVE:
            flash('您的账号尚未激活', 'warning')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def owner_required(model_class, id_param='id'):
    """资源所有者权限装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('请先登录', 'info')
                return redirect(url_for('auth.login'))
            
            # 检查用户状态
            if current_user.Status == UserStatus.BANNED:
                flash('您的账号已被封禁', 'danger')
                return redirect(url_for('auth.login'))
            
            # 获取资源ID
            resource_id = kwargs.get(id_param)
            if not resource_id:
                flash('无效的请求', 'danger')
                return redirect(url_for('main.index'))
            
            # 查找资源
            resource = model_class.query.get(resource_id)
            if not resource:
                flash('资源不存在', 'danger')
                return redirect(url_for('main.index'))
            
            # 检查权限（管理员或资源所有者）
            if current_user.is_admin() or getattr(resource, 'UserID', None) == current_user.UserID:
                return f(*args, **kwargs)
            
            flash('您没有权限操作此资源', 'danger')
            return redirect(url_for('main.index'))
        return decorated_function
    return decorator

def can_post_required(f):
    """检查用户是否可以发帖的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'info')
            return redirect(url_for('auth.login'))
        
        if not current_user.can_post():
            flash('您没有权限发布帖子', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def can_comment_required(f):
    """检查用户是否可以评论的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'info')
            return redirect(url_for('auth.login'))
        
        if not current_user.can_comment():
            flash('您没有权限发表评论', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function