from flask import render_template, Blueprint, jsonify, request
from flask_login import login_required
from ..models import User, Post, Comment, Category, Tag, db
from .. import cache
from sqlalchemy import func, desc
from datetime import datetime, date, timedelta

# 创建分析平台的Blueprint
analytics = Blueprint('analytics', __name__)

@analytics.route('/')
def analytics_dashboard():
    """分析平台首页"""
    return render_template('analytics/dashboard.html', title='数据分析平台')

@analytics.route('/stats')
def analytics_stats():
    """获取分析平台所需的统计数据"""
    # 总用户数
    total_users = User.query.count()
    
    # 活跃用户数（Status为active的用户）
    active_users = User.query.filter_by(Status='active').count()
    
    # 总帖子数
    total_posts = Post.query.count()
    
    # 活跃帖子数
    active_posts = Post.query.filter_by(Status='active').count()
    
    # 总评论数
    total_comments = Comment.query.count()
    
    # 已批准评论数
    approved_comments = Comment.query.filter_by(Status='approved').count()
    
    # 今日新增帖子数
    today = date.today()
    today_posts = Post.query.filter(
        func.date(Post.CreationTime) == today,
        Post.Status == 'active'
    ).count()
    
    # 最近7天的帖子趋势
    daily_posts = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        count = Post.query.filter(
            func.date(Post.CreationTime) == day,
            Post.Status == 'active'
        ).count()
        daily_posts.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # 各分类帖子数量统计
    # 现在使用Post.CategoryID直接关联Category表
    category_stats = db.session.query(
        Category.CategoryName,
        func.count(Post.PostID).label('post_count')
    ).join(
        Post, Category.id == Post.CategoryID
    ).filter(
        Post.Status == 'active'
    ).group_by(
        Category.CategoryID
    ).all()
    
    # 热门标签统计
    tag_stats = Tag.query.order_by(desc(Tag.UsageCount)).limit(10).all()
    
    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'total_posts': total_posts,
        'active_posts': active_posts,
        'total_comments': total_comments,
        'approved_comments': approved_comments,
        'today_posts': today_posts,
        'daily_posts': daily_posts,
        'category_stats': [{
            'category': stat.CategoryName,
            'count': stat.post_count
        } for stat in category_stats],
        'tag_stats': [{
            'tag': tag.TagName,
            'count': tag.UsageCount
        } for tag in tag_stats]
    })
