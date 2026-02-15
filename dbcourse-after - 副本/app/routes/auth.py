from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import logging
from werkzeug.utils import secure_filename
import os
from app.models import Treet_IP_Conn, User
from app.models.user import UserStatus
from app.forms import RegistrationForm, LoginForm

# 配置日志
logger = logging.getLogger(__name__)

# 创建认证蓝图
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    logger.info("===== 进入注册函数 =====")
    if current_user.is_authenticated:
        logger.info("用户已认证，重定向到首页")
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    logger.info(f"表单初始化完成")
    
    if form.validate_on_submit():
        logger.info(f"表单验证通过: username={form.username.data}")
        # 创建新用户
        new_user = User(
            UserName=form.username.data,
            UserEmail=None
        )
        new_user.set_password(form.password.data)
        new_user.Reputation = 10  # 新用户初始声望值
        
        logger.info(f"用户对象创建: 用户名: {new_user.UserName}, 邮箱: {new_user.UserEmail}")
        
        try:
            logger.info("准备添加用户到数据库会话")
            Treet_IP_Conn.session.add(new_user)
            logger.info("用户已添加到会话")
            
            # 检查会话中是否有该用户
            logger.info(f"会话中未提交的新增对象数量: {len(Treet_IP_Conn.session.new)}")
            
            # 检查数据库连接状态
            logger.info(f"数据库连接状态: {Treet_IP_Conn.engine.pool.status()}")
            
            logger.info("准备提交数据库会话")
            Treet_IP_Conn.session.commit()
            logger.info(f"数据库提交成功！用户ID: {new_user.UserID}")
            
            # 验证用户是否真的存储在数据库中
            Treet_IP_Conn.session.expire_all()  # 清空会话缓存
            saved_user = User.query.filter_by(UserName=form.username.data).first()
            if saved_user:
                logger.info(f"验证成功: 用户已成功存储到数据库，ID: {saved_user.UserID}")
            else:
                logger.warning("警告: 数据库中未找到刚刚注册的用户！")
            
            flash('注册成功，已获得10点初始声望值，请登录', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            logger.error(f"数据库错误: {type(e).__name__}: {str(e)}")
            logger.error(f"错误详情: {repr(e)}")
            import traceback
            traceback.print_exc()
            Treet_IP_Conn.session.rollback()
            logger.error("数据库会话已回滚")
            flash(f'注册失败: {str(e)}', 'danger')
    elif request.method == 'POST':
        logger.warning(f"表单验证失败: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                logger.warning(f"字段 {field}: {error}")
    
    return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # 查找用户
        user = User.query.filter_by(UserName=form.username.data).first()
        
        # 详细记录登录过程
        logger.info(f"登录尝试 - 用户名: {form.username.data}, 用户是否存在: {user is not None}")
        
        # 验证用户和密码
        if user:
            logger.info(f"用户存在 - 状态: {user.Status}, ID: {user.UserID}")
            # 检查用户状态
            if user.Status == UserStatus.BANNED:
                logger.info("用户账号已被封禁")
                flash('您的账号已被封禁', 'danger')
                return render_template('auth/login.html', form=form)
            
            if user.Status == UserStatus.INACTIVE:
                logger.info("用户账号尚未激活")
                flash('您的账号尚未激活', 'warning')
                return render_template('auth/login.html', form=form)
                
            # 验证密码
            password_valid = user.check_password(form.password.data)
            logger.info(f"密码验证结果: {password_valid}")
            
            if password_valid:
                logger.info("密码验证成功，登录用户")
                login_user(user, remember=form.remember.data)
                # 更新最后登录时间
                user.LastLoginTime = datetime.utcnow()
                Treet_IP_Conn.session.commit()
                # 如果有next参数，重定向到next页面，否则重定向到首页
                next_page = request.args.get('next')
                logger.info(f"登录成功，重定向到: {next_page or '首页'}")
                return redirect(next_page or url_for('main.index'))
        
        logger.info("登录失败 - 用户名或密码错误")
        flash('用户名或密码错误', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """用户注销"""
    # 记录注销时间
    current_user.LastLoginTime = datetime.utcnow()
    Treet_IP_Conn.session.commit()
    logout_user()
    flash('已成功注销', 'success')
    return redirect(url_for('main.index'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """用户个人资料"""
    from app.forms import ProfileForm
    # 初始化表单，不传入邮箱参数
    form = ProfileForm()
    
    # 手动设置 UserBio 字段的值
    if request.method == 'GET':
        form.UserBio.data = current_user.UserBio or ''
    
    if form.validate_on_submit():
        # 更新用户信息（移除邮箱更新）
        current_user.UserBio = form.UserBio.data or ''
        
        # 处理头像上传
        if form.avatar_file.data:
            file = form.avatar_file.data
            filename = secure_filename(file.filename)
            if filename:
                ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"avatar_{current_user.UserID}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}"
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
                
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(upload_path)
                current_user.AvatarURL = url_for('static', filename=f'uploads/{new_filename}')
        
        current_user.LastLoginTime = datetime.utcnow()
        
        try:
            Treet_IP_Conn.session.commit()
            flash('个人资料已更新', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            Treet_IP_Conn.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')
    
    # 预先查询并排序用户的帖子
    from app.models import Post
    user_posts = current_user.posts.order_by(Post.CreationTime.desc()).all()
    return render_template('auth/profile.html', user=current_user, form=form, posts=user_posts)

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """忘记密码页面"""
    from app.forms import ForgotPasswordForm
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        # 查找用户
        user = User.query.filter_by(UserEmail=form.email.data).first()
        if user:
            # 生成重置密码令牌
            token = user.generate_token(expiration=3600)  # 1小时内有效
            # 这里可以实现发送重置密码邮件的逻辑
            # 为了演示，我们将令牌显示在页面上
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            flash(f'重置密码链接: {reset_link}', 'info')
            flash('在实际应用中，此链接将发送到您的邮箱', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密码页面"""
    from app.forms import ResetPasswordForm
    # 验证令牌
    user = User.verify_token(token)
    if not user:
        flash('无效或已过期的令牌', 'danger')
        return redirect(url_for('auth.login'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # 设置新密码
        user.set_password(form.password.data)
        user.LastLoginTime = datetime.utcnow()
        
        try:
            Treet_IP_Conn.session.commit()
            flash('密码已成功重置，请使用新密码登录', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            Treet_IP_Conn.session.rollback()
            flash(f'重置密码失败: {str(e)}', 'danger')
    
    return render_template('auth/reset_password.html', form=form)

@auth.route('/admin_reset', methods=['GET', 'POST'])
def admin_reset():
    """重置管理员密码（紧急功能）"""
    from app.forms import ResetPasswordForm
    from app.models.user import UserRole
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # 查找管理员账号
        admin_user = User.query.filter_by(Role=UserRole.ADMIN).first()
        
        if admin_user:
            # 设置新密码
            admin_user.set_password(form.password.data)
            admin_user.LastLoginTime = datetime.utcnow()
            
            try:
                Treet_IP_Conn.session.commit()
                flash('管理员密码已成功重置，请使用新密码登录', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                Treet_IP_Conn.session.rollback()
                flash(f'重置密码失败: {str(e)}', 'danger')
        else:
            # 如果没有管理员账号，创建一个新的
            new_admin = User(
                UserName='admin',
                UserEmail=None
            )
            new_admin.set_password(form.password.data)
            new_admin.Role = UserRole.ADMIN
            new_admin.Status = UserStatus.ACTIVE
            new_admin.Reputation = 100
            
            try:
                Treet_IP_Conn.session.add(new_admin)
                Treet_IP_Conn.session.commit()
                flash('管理员账号不存在，已创建新的管理员账号，用户名: admin', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                Treet_IP_Conn.session.rollback()
                flash(f'创建管理员账号失败: {str(e)}', 'danger')
    
    return render_template('auth/reset_password.html', form=form)