from flask import render_template, Blueprint, redirect, url_for, request, flash
from flask_login import login_required
from app.models import Treet_IP_Conn, Category
from functools import wraps
from flask_login import current_user

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (hasattr(current_user, 'is_admin') and current_user.is_admin()):
            flash('您没有权限访问此页面', 'danger')
            return redirect(url_for('forum.forum_index'))
        return f(*args, **kwargs)
    return decorated_function

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """首页 - 重定向到论坛"""
    return redirect(url_for('forum.forum_index'))



# 分类管理相关路由
@main.route('/admin/categories')
@admin_required
def admin_categories():    
    categories = Category.query.all()
    return render_template('admin/categories.html', title='管理分类', categories=categories)




@main.route('/admin/categories/create', methods=['GET', 'POST'])
@admin_required
def create_category():
    """创建分类"""
    if request.method == 'POST':
        category_name = request.form.get('CategoryName', '').strip()
        description = request.form.get('Description', '').strip()
        
        if not category_name:
            flash('分类名称不能为空', 'danger')
            return redirect(url_for('main.create_category'))
        
        # 检查分类是否已存在
        if Category.query.filter_by(CategoryName=category_name).first():
            flash('分类已存在', 'warning')
            return redirect(url_for('main.create_category'))
        
        # 创建新分类
        new_category = Category(
            CategoryName=category_name,
            Description=description
        )
        
        try:
            Treet_IP_Conn.session.add(new_category)
            Treet_IP_Conn.session.commit()
            flash('分类创建成功', 'success')
            return redirect(url_for('main.admin_categories'))
        except Exception as e:
            Treet_IP_Conn.session.rollback()
            flash(f'创建失败: {str(e)}', 'danger')
    
    return render_template('admin/category_form.html', title='创建分类')


@main.route('/admin/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    """编辑分类"""
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        category_name = request.form.get('CategoryName', '').strip()
        description = request.form.get('Description', '').strip()
        
        if not category_name:
            flash('分类名称不能为空', 'danger')
            return redirect(url_for('main.edit_category', category_id=category_id))
        
        # 检查分类名是否与其他分类重复
        existing = Category.query.filter(
            Category.CategoryName == category_name,
            Category.CategoryID != category_id
        ).first()
        
        if existing:
            flash('分类名称已存在', 'warning')
            return redirect(url_for('main.edit_category', category_id=category_id))
        
        # 更新分类信息
        category.CategoryName = category_name
        category.Description = description
        
        try:
            Treet_IP_Conn.session.commit()
            flash('分类更新成功', 'success')
            return redirect(url_for('main.admin_categories'))
        except Exception as e:
            Treet_IP_Conn.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')
    
    return render_template('admin/category_form.html', title='编辑分类', category=category)


@main.route('/admin/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id):
    """删除分类"""
    category = Category.query.get_or_404(category_id)
    
    # 检查是否有帖子使用该分类
    if category.posts.count() > 0:
        flash('该分类下有帖子，无法删除', 'warning')
        return redirect(url_for('main.admin_categories'))
    
    try:
        Treet_IP_Conn.session.delete(category)
        Treet_IP_Conn.session.commit()
        flash('分类删除成功', 'success')
    except Exception as e:
        Treet_IP_Conn.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')
    
    return redirect(url_for('main.admin_categories'))