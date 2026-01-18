from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, Category
from datetime import datetime

class RegistrationForm(FlaskForm):
    """用户注册表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=3, max=50, message='用户名长度必须在3-50个字符之间')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=6, message='密码长度至少为6个字符')
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('注册')
    
    def validate_username(self, username):
        """验证用户名是否已存在"""
        user = User.query.filter_by(UserName=username.data).first()
        if user:
            raise ValidationError('该用户名已被注册，请选择其他用户名')

class LoginForm(FlaskForm):
    """用户登录表单"""
    username = StringField('用户名', validators=[DataRequired(message='用户名不能为空')])
    password = PasswordField('密码', validators=[DataRequired(message='密码不能为空')])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

class PostForm(FlaskForm):
    """帖子创建/编辑表单"""
    title = StringField('标题', validators=[
        DataRequired(message='标题不能为空'),
        Length(min=5, max=200, message='标题长度必须在5-200个字符之间')
    ])
    category = SelectField('分类', coerce=int, validators=[DataRequired(message='请选择分类')])
    content = TextAreaField('内容', validators=[DataRequired(message='内容不能为空')])
    tags = StringField('标签', validators=[Length(max=200, message='标签长度不能超过200个字符')])
    submit = SubmitField('发布')
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # 动态加载分类选项
        self.category.choices = [(cat.CategoryID, cat.CategoryName) for cat in Category.query.all()]
        if not self.category.choices:
            self.category.choices = [(0, '未分类')]

class CommentForm(FlaskForm):
    """评论表单"""
    content = TextAreaField('评论内容', validators=[
        DataRequired(message='评论内容不能为空'),
        Length(min=1, max=1000, message='评论长度必须在1-1000个字符之间')
    ])
    parent_id = HiddenField('父评论ID')
    submit = SubmitField('发表评论')

class ProfileForm(FlaskForm):
    """用户资料编辑表单"""
    UserBio = TextAreaField('个人简介', validators=[Length(max=500, message='个人简介不能超过500个字符')])
    AvatarURL = StringField('头像URL', validators=[Length(max=255, message='头像URL不能超过255个字符')])
    submit = SubmitField('更新资料')
    
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

class ForgotPasswordForm(FlaskForm):
    """忘记密码表单"""
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址')
    ])
    submit = SubmitField('发送重置链接')
    
    def validate_email(self, email):
        """验证邮箱是否存在"""
        user = User.query.filter_by(UserEmail=email.data).first()
        if not user:
            raise ValidationError('该邮箱未注册')

class ResetPasswordForm(FlaskForm):
    """重置密码表单"""
    password = PasswordField('新密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=8, message='密码长度至少为8个字符'),
        EqualTo('confirm_password', message='两次输入的密码不一致')
    ])
    confirm_password = PasswordField('确认新密码', validators=[
        DataRequired(message='请确认密码')
    ])
    submit = SubmitField('重置密码')