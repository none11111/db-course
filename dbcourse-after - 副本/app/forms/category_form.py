from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class CategoryForm(FlaskForm):
    """分类表单类，用于创建和编辑分类"""
    category_name = StringField('分类名称', validators=[
        DataRequired(message='分类名称不能为空'),
        Length(min=2, max=100, message='分类名称长度必须在2-100个字符之间')
    ])
    description = TextAreaField('分类描述', validators=[
        Length(max=500, message='分类描述不能超过500个字符')
    ])
    is_active = BooleanField('是否启用', default=True)
    submit = SubmitField('保存')
