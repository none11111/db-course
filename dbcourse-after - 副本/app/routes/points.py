from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.services.point_service import PointService
from app.models.points import PointRecord, PointShopItem, PointRedemption, PointActionType
from app import Treet_IP_Conn
from datetime import datetime, date
from functools import wraps

points = Blueprint('points', __name__)

def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models.user import UserRole
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.Role != UserRole.ADMIN:
            flash('需要管理员权限', 'danger')
            return redirect(url_for('forum.forum'))
        return f(*args, **kwargs)
    return decorated_function

@points.route('/points')
@login_required
def points_index():
    """积分中心首页"""
    user = current_user
    
    # 获取最近的积分记录
    recent_records = PointRecord.query.filter_by(UserID=user.UserID).order_by(
        PointRecord.CreationTime.desc()
    ).limit(20).all()
    
    # 获取积分商城商品
    shop_items = PointShopItem.query.filter_by(IsActive=True).order_by(
        PointShopItem.PointsRequired.asc()
    ).all()
    
    # 获取兑换记录
    redemptions = PointRedemption.query.filter_by(UserID=user.UserID).order_by(
        PointRedemption.RedemptionTime.desc()
    ).limit(10).all()
    
    return render_template('points/index.html', 
                         title='积分中心',
                         user=user,
                         recent_records=recent_records,
                         shop_items=shop_items,
                         redemptions=redemptions)

@points.route('/points/checkin', methods=['POST'])
@login_required
def check_in():
    """每日签到"""
    success, message = PointService.check_in(current_user.UserID)
    return jsonify({
        'success': success,
        'message': message,
        'consecutive_days': current_user.ConsecutiveCheckInDays or 0,
        'points': current_user.Points or 0
    })

@points.route('/points/complete_profile', methods=['POST'])
@login_required
def complete_profile():
    """完善个人资料"""
    success, message = PointService.complete_profile(current_user.UserID)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(url_for('auth.profile', user_id=current_user.UserID))

@points.route('/points/bind_phone', methods=['POST'])
@login_required
def bind_phone():
    """绑定手机"""
    phone = request.form.get('phone')
    if not phone:
        flash('请输入手机号', 'danger')
        return redirect(url_for('auth.profile', user_id=current_user.UserID))
    
    # TODO: 验证手机号格式和发送验证码
    success, message = PointService.bind_phone(current_user.UserID)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(url_for('auth.profile', user_id=current_user.UserID))

@points.route('/points/bind_email', methods=['POST'])
@login_required
def bind_email():
    """绑定邮箱"""
    email = request.form.get('email')
    if not email:
        flash('请输入邮箱', 'danger')
        return redirect(url_for('auth.profile', user_id=current_user.UserID))
    
    # TODO: 验证邮箱格式和发送验证码
    success, message = PointService.bind_email(current_user.UserID)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(url_for('auth.profile', user_id=current_user.UserID))

@points.route('/points/shop')
@login_required
def points_shop():
    """积分商城"""
    items = PointShopItem.query.filter_by(IsActive=True).order_by(
        PointShopItem.PointsRequired.asc()
    ).all()
    
    return render_template('points/shop.html', title='积分商城', items=items)

@points.route('/points/buy/<int:item_id>', methods=['POST'])
@login_required
def buy_item(item_id):
    """购买商品"""
    item = PointShopItem.query.get_or_404(item_id)
    user = current_user
    
    # 检查库存
    if item.Stock != -1 and item.Stock <= 0:
        return jsonify({'success': False, 'message': '商品已售罄'})
    
    # 检查积分是否足够
    if user.Points < item.PointsRequired:
        return jsonify({'success': False, 'message': '积分不足'})
    
    # 扣除积分
    success = PointService.add_points(
        user_id=user.UserID,
        points=-item.PointsRequired,
        action_type=PointActionType.BUY_ITEM,
        description=f'购买商品：{item.ItemName}',
        related_id=item.ItemID
    )
    
    if success:
        # 创建兑换记录
        redemption = PointRedemption(
            UserID=user.UserID,
            ItemID=item.ItemID,
            PointsSpent=item.PointsRequired,
            Status='completed'
        )
        
        # 更新库存
        if item.Stock != -1:
            item.Stock -= 1
        
        Treet_IP_Conn.session.add(redemption)
        Treet_IP_Conn.session.commit()
        
        return jsonify({'success': True, 'message': f'成功购买：{item.ItemName}'})
    else:
        return jsonify({'success': False, 'message': '购买失败'})

@points.route('/points/records')
@login_required
def points_records():
    """积分记录"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    pagination = PointRecord.query.filter_by(UserID=current_user.UserID).order_by(
        PointRecord.CreationTime.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('points/records.html', 
                         title='积分记录',
                         records=pagination)

@points.route('/points/leaderboard')
@login_required
def points_leaderboard():
    """积分排行榜"""
    from app.models.user import User
    
    # 获取积分排行榜
    top_users = User.query.filter(User.Points > 0).order_by(
        User.Points.desc()
    ).limit(100).all()
    
    # 获取本周排行榜
    from sqlalchemy import func, and_
    week_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = week_ago.replace(day=week_ago.day - 7)
    
    weekly_top = PointRecord.query.filter(
        and_(
            PointRecord.CreationTime >= week_ago,
            PointRecord.Points > 0
        )
    ).with_entities(
        PointRecord.UserID,
        func.sum(PointRecord.Points).label('total_points')
    ).group_by(PointRecord.UserID).order_by(
        func.sum(PointRecord.Points).desc()
    ).limit(10).all()
    
    return render_template('points/leaderboard.html',
                         title='积分排行榜',
                         top_users=top_users,
                         weekly_top=weekly_top)
@points.route('/points/api/checkin_status')
@login_required
def checkin_status():
    """获取签到状态（AJAX）"""
    today = date.today()
    from app.models.points import DailyCheckIn
    
    checked_in = DailyCheckIn.query.filter_by(
        UserID=current_user.UserID,
        CheckInDate=today
    ).first() is not None
    
    return jsonify({
        'checked_in': checked_in,
        'consecutive_days': current_user.ConsecutiveCheckInDays or 0,
        'points': current_user.Points or 0
    })

@points.route('/admin/shop')
@admin_required
def admin_shop():
    """管理员商品管理页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    pagination = PointShopItem.query.order_by(
        PointShopItem.CreationTime.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('points/admin_shop.html', 
                         title='商品管理',
                         pagination=pagination)

@points.route('/admin/shop/add', methods=['GET', 'POST'])
@admin_required
def admin_add_item():
    """管理员添加商品"""
    from app.forms import ShopItemForm
    
    form = ShopItemForm()
    
    if form.validate_on_submit():
        image_url = None
        
        if form.image_file.data:
            file = form.image_file.data
            filename = secure_filename(file.filename)
            if filename:
                ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"item_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}"
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
                
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(upload_path)
                image_url = url_for('static', filename=f'uploads/{new_filename}')
        
        item = PointShopItem(
            ItemName=form.item_name.data,
            ItemDescription=form.description.data,
            PointsRequired=form.points_required.data,
            Stock=form.stock.data,
            ImageURL=image_url,
            ItemType=form.category.data,
            IsActive=form.is_active.data
        )
        
        Treet_IP_Conn.session.add(item)
        Treet_IP_Conn.session.commit()
        
        flash('商品添加成功', 'success')
        return redirect(url_for('points.admin_shop'))
    
    return render_template('points/admin_item_form.html',
                         title='添加商品',
                         form=form,
                         action='add')

@points.route('/admin/shop/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_item(item_id):
    """管理员编辑商品"""
    from app.forms import ShopItemForm
    
    item = PointShopItem.query.get_or_404(item_id)
    form = ShopItemForm(obj=item)
    
    if form.validate_on_submit():
        item.ItemName = form.item_name.data
        item.ItemDescription = form.description.data
        item.PointsRequired = form.points_required.data
        item.Stock = form.stock.data
        item.ItemType = form.category.data
        item.IsActive = form.is_active.data
        
        if form.image_file.data:
            file = form.image_file.data
            filename = secure_filename(file.filename)
            if filename:
                ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"item_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}"
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
                
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(upload_path)
                item.ImageURL = url_for('static', filename=f'uploads/{new_filename}')
        
        Treet_IP_Conn.session.commit()
        
        flash('商品更新成功', 'success')
        return redirect(url_for('points.admin_shop'))
    
    return render_template('points/admin_item_form.html',
                         title='编辑商品',
                         form=form,
                         item=item,
                         action='edit')

@points.route('/admin/shop/delete/<int:item_id>', methods=['POST'])
@admin_required
def admin_delete_item(item_id):
    """管理员删除商品"""
    item = PointShopItem.query.get_or_404(item_id)
    
    # 检查是否有兑换记录
    redemption_count = PointRedemption.query.filter_by(ItemID=item_id).count()
    if redemption_count > 0:
        flash('该商品已有兑换记录，无法删除', 'danger')
        return redirect(url_for('points.admin_shop'))
    
    Treet_IP_Conn.session.delete(item)
    Treet_IP_Conn.session.commit()
    
    flash('商品删除成功', 'success')
    return redirect(url_for('points.admin_shop'))

@points.route('/admin/shop/toggle/<int:item_id>', methods=['POST'])
@admin_required
def admin_toggle_item(item_id):
    """管理员切换商品状态"""
    item = PointShopItem.query.get_or_404(item_id)
    item.IsActive = not item.IsActive
    Treet_IP_Conn.session.commit()
    
    status = '上架' if item.IsActive else '下架'
    flash(f'商品已{status}', 'success')
    return redirect(url_for('points.admin_shop'))

@points.route('/admin/redemptions')
@admin_required
def admin_redemptions():
    """管理员查看兑换记录"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    from app.models.user import User
    
    pagination = PointRedemption.query.options(
        Treet_IP_Conn.joinedload(PointRedemption.user),
        Treet_IP_Conn.joinedload(PointRedemption.item)
    ).order_by(
        PointRedemption.RedemptionTime.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('points/admin_redemptions.html',
                         title='兑换记录',
                         pagination=pagination)
