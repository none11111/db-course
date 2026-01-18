from flask import render_template, Blueprint, redirect, url_for, request, flash, g, jsonify
from flask_login import current_user, login_required
from datetime import datetime, date
from sqlalchemy import func, desc
from functools import wraps
from ..models import Treet_IP_Conn, Post, User, Comment, Category, Tag, UserStatus, UserRole
from ..models.post import posttags  # 导入posttags表定义
from ..forms import PostForm, CommentForm
from .. import cache
from ..utils.db_utils import get_forum_statistics
import json
# 显式导入OpenAI客户端
from openai import OpenAI, OpenAIError
import os

# ========== 核心修复：正确初始化OpenAI客户端 ==========
# 建议从环境变量读取API Key（安全），本地测试可临时写死
client = OpenAI(
    api_key="sk-c891db66789b49018757f897c6676da1",  # 你的API Key
    base_url="https://api.deepseek.com/v1"  # DeepSeek固定端点
)

def ai_content_check(post_content):
    """
    使用AI进行内容审核
    :param post_content: 要审核的内容
    :return: True表示内容合规，False表示内容违规
    """
    try:
        print(f"开始AI审核，内容: {post_content[:50]}...")
        
        # ========== 修复1：使用正确的模型名 ==========
        response = client.chat.completions.create(
            model="deepseek-chat",  # 替换为官方标准模型名
            messages=[
                {"role": "system", "content": "你是论坛内容审核员，严格检查内容是否包含违规行为。\n违规类型：1.脏话/粗口 2.人身攻击 3.政治敏感 4.色情淫秽 5.广告营销 6.ILLEGAL 7.虚假信息 8.侵权\n审核规则：只要存在任何违规内容返回1，完全合规返回0，仅返回数字，无其他字符。"},
                {"role": "user", "content": post_content}
            ],
            temperature=0,  # 关闭随机性
            max_tokens=2,  # 放宽1个字符冗余，避免模型返回异常
            timeout=10,  # 添加超时设置（防止请求挂起）
        )
        
        print(f"AI响应原始数据: {response}")
        # ========== 修复2：健壮的结果处理 ==========
        result = response.choices[0].message.content.strip()  # 去除空格/换行
        print(f"AI审核结果(清洗后): {result}, 原始内容: {post_content[:50]}...")
        
        # 兼容模型可能返回的异常格式（如"违规"→强制返回1，避免误判）
        if result not in ["0", "1"]:
            print(f"模型返回非预期结果: {result}，默认判定违规")
            return False
        
        # 返回True=合规，False=违规
        return result == "0"
    
    # ========== 修复3：更详细的错误捕获 ==========
    except OpenAIError as e:
        error_detail = {
            "error_type": type(e).__name__,
            "error_code": getattr(e, 'code', '未知'),
            "error_message": str(e),
            "request_content": post_content[:50]
        }
        print(f"OpenAI API错误: {json.dumps(error_detail, ensure_ascii=False)}")
        # API调用失败默认拦截（避免违规内容通过）
        return False
    except Exception as e:
        print(f"AI审核意外错误: {type(e).__name__}, 错误信息: {e}")
        import traceback
        traceback.print_exc()
        return False

forum = Blueprint('forum', __name__)

# 装饰器函数
def user_required(f):
    """用户登录权限装饰器"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

@forum.route('/forum')
def forum_index():
    """论坛首页"""
    # 获取筛选参数
    category_id = request.args.get('category', type=int)
    tag_id = request.args.get('tag', type=int)
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'latest')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 构建查询 - 显示已审核通过(approved)和旧版活跃(active)状态的帖子
    query = Treet_IP_Conn.session.query(Post).options(Treet_IP_Conn.joinedload(Post.author)).filter(Post.Status.in_(['approved', 'active']))
    
    # 分类筛选
    if category_id:
        query = query.join(Post.categories).filter(Category.CategoryID == category_id)
    
    # 标签筛选
    if tag_id:
        query = query.join(Post.tags).filter(Tag.TagID == tag_id)
    
    # 搜索筛选
    if search_query:
        search_pattern = f'%{search_query}%'
        query = query.filter(
            (Post.PostTitle.like(search_pattern)) |
            (Post.PostContent.like(search_pattern))
        )
    
    # 排序
    if sort_by == 'latest':
        query = query.order_by(Post.CreationTime.desc())
    elif sort_by == 'popular':
        query = query.order_by(Post.ViewCount.desc())
    elif sort_by == 'comments':
        # 使用子查询计算每个帖子的评论数并排序
        # 子查询获取每个帖子的评论计数
        comment_count_subquery = Treet_IP_Conn.session.query(
            Comment.PostID,
            func.count(Comment.CommentID).label('comment_count')
        ).group_by(Comment.PostID).subquery()
        # 连接子查询并按评论数排序
        query = query.outerjoin(
            comment_count_subquery,
            Post.PostID == comment_count_subquery.c.PostID
        ).order_by(func.coalesce(comment_count_subquery.c.comment_count, 0).desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items
    
    # 获取分类列表
    categories = Treet_IP_Conn.session.query(Category).all()
    
    # 计算每个分类的帖子数量
    category_post_counts = {}
    for category in categories:
        post_count = Treet_IP_Conn.session.query(Post).filter(
            Post.categories.any(Category.CategoryID == category.CategoryID),
            Post.Status.in_(['approved', 'active'])
        ).count()
        category_post_counts[category.CategoryID] = post_count
    
    # 获取热门标签
    popular_tags = Treet_IP_Conn.session.query(Tag).order_by(Treet_IP_Conn. desc(Tag.UsageCount)).limit(10).all()
    
    # 统计数据 - 使用新的数据分析工具
    stats = get_forum_statistics()
    user_count = stats['user_count']
    post_count = stats['post_count']
    comment_count = stats['comment_count']
    today_post_count = stats['today_post_count']
    
    return render_template('forum/index.html', 
                           title='论坛', 
                           posts=posts, 
                           pagination=pagination, 
                           categories=categories,
                           category_post_counts=category_post_counts,
                           popular_tags=popular_tags,
                           category_id=category_id,
                           tag_id=tag_id,
                           search_query=search_query,
                           sort_by=sort_by,
                           user_count=user_count,
                           post_count=post_count,
                           comment_count=comment_count,
                           today_post_count=today_post_count)

@forum.route('/forum/create_post', methods=['GET', 'POST'])
@user_required
def create_post():
    """创建新帖子"""
    print(f"请求方法: {request.method}")
    print(f"请求数据: {request.form if request.method == 'POST' else 'N/A'}")
    
    form = PostForm()
    print(f"表单初始化完成，分类选项: {form.category.choices}")
    
    # 确保分类选项存在
    if not form.category.choices or form.category.choices[0][0] == 0:
        print("没有有效的分类选项，创建默认分类")
            # 创建默认分类
        default_category = Category.query.filter_by(CategoryName='未分类').first()
        if not default_category:
            print("创建新的默认分类")
            default_category = Category(CategoryName='未分类', CategoryDescription='默认分类')
            Treet_IP_Conn.session.add(default_category)
            Treet_IP_Conn.session.commit()
        # 更新表单选项
        form.category.choices = [(default_category.CategoryID, default_category.CategoryName)]
        form.category.data = default_category.CategoryID
        print(f"更新后的分类选项: {form.category.choices}, 选中值: {form.category.data}")
    
    if form.validate_on_submit():
        print(f"表单验证通过: title={form.title.data}, category={form.category.data}")
        # 创建新帖子
        # 检查current_user的属性名
        user_id_value = getattr(current_user, 'UserID', None)
        if not user_id_value:
            user_id_value = getattr(current_user, 'id', None)
        print(f"用户ID值: {user_id_value}, 用户对象属性: {dir(current_user)}")
        
        # 进行AI内容审核
        post_content = form.title.data + "\n" + form.content.data
        is_approved = ai_content_check(post_content)
        
        # 根据审核结果设置帖子状态
        status = 'approved' if is_approved else 'pending'  # AI审核不通过时设置为待人工审核
        
        new_post = Post(
            PostTitle=form.title.data,
            PostContent=form.content.data,
            CreationTime=datetime.utcnow(),
            UserID=user_id_value,  # 使用UserID字段
            Status=status,  # 根据AI审核结果设置状态
            AIAuditResult=is_approved,
            AIAuditTime=datetime.utcnow(),
            IsAIAudit=True
        )
        print(f"创建新帖子对象: {new_post.PostTitle}")
        
        # 处理分类
        if form.category.data and form.category.data > 0:
            category = Category.query.get(form.category.data)
            if category:
                new_post.categories.append(category)
                print(f"添加分类: {category.CategoryName}")
            else:
                print(f"警告: 未找到分类ID={form.category.data}")
        
        # 处理标签
        tag_processed = False
        if form.tags.data:
            tag_processed = True
            tag_names = [tag.strip() for tag in form.tags.data.split(',')]
            print(f"处理标签: {tag_names}")
            for tag_name in tag_names:
                if tag_name:
                    # 查找或创建标签
                    tag = Tag.query.filter_by(TagName=tag_name).first()
                    if not tag:
                        tag = Tag(TagName=tag_name, UsageCount=1)
                        Treet_IP_Conn.session.add(tag)
                        print(f"创建新标签: {tag_name}")
                    else:
                        tag.UsageCount += 1
                        print(f"更新标签使用次数: {tag_name}")
                    new_post.tags.append(tag)
        
        try:
            print(f"准备添加帖子到数据库")
            Treet_IP_Conn.session.add(new_post)
            print(f"准备提交事务")
            Treet_IP_Conn.session.commit()
            print(f"帖子提交成功，状态: {new_post.Status}, ID={new_post.PostID}")
            
            # 根据审核结果显示不同的提示信息
            if new_post.Status == 'approved':
                flash('帖子发布成功！', 'success')
            else:
                flash('帖子内容正在等待人工审核，请耐心等待。', 'info')
                
            return redirect(url_for('forum.forum_index'))
        except Exception as e:
            Treet_IP_Conn.session.rollback()
            error_msg = f'发布失败: {str(e)}'
            print(error_msg)
            flash(error_msg, 'danger')
    elif request.method == 'POST':
        # 表单验证失败
        print(f"表单验证失败: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text} - {error}', 'danger')
    
    # GET请求 - 显示创建表单
    print(f"返回创建帖子表单")
    return render_template('forum/create_post.html', title='发布帖子', form=form)

@forum.route('/forum/post/<int:post_id>')
def post_detail(post_id):
    # 尝试从缓存获取
    cache_key = f'post_detail_{post_id}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        post, root_comments, categories = cached_data
        g._from_cache = True
        # 将缓存的ORM对象重新附加到当前会话
        Treet_IP_Conn.session.add(post)
        for comment in root_comments:
            Treet_IP_Conn.session.add(comment)
            # 简单循环处理回复，避免递归函数
            for reply in comment.replies:
                Treet_IP_Conn.session.add(reply)
                for subreply in reply.replies:
                    Treet_IP_Conn.session.add(subreply)
        for category in categories:
            Treet_IP_Conn.session.add(category)
    else:
        g._from_cache = False
        """帖子详情页面"""
        # 获取帖子
        post = Treet_IP_Conn.session.query(Post).options(Treet_IP_Conn.joinedload(Post.author), Treet_IP_Conn.joinedload(Post.categories), Treet_IP_Conn.joinedload(Post.tags)).get_or_404(post_id)
        
        # 更新浏览量
        post.ViewCount = (post.ViewCount or 0) + 1
        Treet_IP_Conn.session.commit()
        
        # 只获取顶级评论，预加载作者和直接回复
        root_comments = Comment.query.options(
            Treet_IP_Conn.joinedload(Comment.author),
            Treet_IP_Conn.joinedload(Comment.replies).joinedload(Comment.author)
        ).filter_by(PostID=post_id, ParentCommentID=None, Status='approved').order_by(Comment.CreationTime.desc()).all()
        # 手动加载二级回复和三级回复
        for comment in root_comments:
            for reply in comment.replies:
                reply.replies =     Comment.query.filter_by(ParentCommentID=reply.CommentID, Status='approved').options(
                    Treet_IP_Conn.joinedload(Comment.author)
                ).all()
                # 加载三级回复
                for subreply in reply.replies:
                    subreply.replies = Comment.query.filter_by(ParentCommentID=subreply.CommentID, Status='approved').options(
                        Treet_IP_Conn.joinedload(Comment.author)
                    ).all()
        
        # 获取分类列表
        categories =Category.query.all()
        
        # 缓存数据
        cache.set(cache_key, (post, root_comments, categories), timeout=300)
    
    # 每次请求都重新创建评论表单，不使用缓存
    form = CommentForm()
    
    return render_template('forum/post_detail.html', title=post.PostTitle, post=post, comments=root_comments, categories=categories, form=form)

@forum.route('/forum/post/<int:post_id>/comment', methods=['POST'])
@user_required
def add_comment(post_id):
    """添加评论"""
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        # 获取父评论ID（如果是回复）
        parent_id = form.parent_id.data if form.parent_id.data else None
        
        # 如果有父评论ID，检查它是否存在且属于同一帖子
        if parent_id:
            parent_comment = Comment.query.get(parent_id)
            if not parent_comment or parent_comment.PostID != post_id:
                flash('父评论不存在或不属于当前帖子', 'danger')
                return redirect(url_for('forum.post_detail', post_id=post_id))
        
        # 进行AI内容审核
        comment_content = form.content.data
        is_approved = ai_content_check(comment_content)
        
        # 根据审核结果设置评论状态
        status = 'approved' if is_approved else 'pending'  # AI审核不通过时设置为待人工审核  # AI审核不通过时设置为待人工审核'pending'
        
        # 创建评论，包含AI审核信息
        comment = Comment(
            CommentContent=form.content.data,
            CreationTime=datetime.utcnow(),
            UserID=current_user.UserID,
            PostID=post_id,
            ParentCommentID=parent_id,
            Status=status,
            AIAuditResult=is_approved,
            AIAuditTime=datetime.utcnow(),
            IsAIAudit=True
        )
     
        Treet_IP_Conn.session.add(comment)
        Treet_IP_Conn.session.commit()
        
        # 如果评论被批准，更新作者声望
        if comment.Status == 'approved' and post.UserID != current_user.UserID:
            post_author = User.query.get(post.UserID)
            if post_author:
                post_author.Reputation = (post_author.Reputation or 0) + 1
                Treet_IP_Conn.session.commit()
        
        # 根据审核结果显示不同的提示信息
        if comment.Status != 'approved':
            flash('评论内容正在等待人工审核，请耐心等待。', 'info')
        
        # 更新帖子评论数
        if hasattr(post, 'CommentCount'):
            post.CommentCount = (post.CommentCount or 0) + 1
            Treet_IP_Conn.session.commit()
        
        # 清除相关缓存
        clear_cache_for_post(post_id)
        
        # 根据是否有父评论显示不同的成功消息
        if parent_id:
            flash('回复成功', 'success')
        else:
            flash('评论成功', 'success')
    else:
        # 表单验证失败
        flash('评论内容不能为空', 'danger')
    
    return redirect(url_for('forum.post_detail', post_id=post_id))



@forum.route('/forum/moderation')
@user_required
def moderation():
    """管理员审核页面"""
    if not current_user.is_admin():
        flash('你没有权限访问此页面', 'danger')
        return redirect(url_for('forum.forum_index'))
    
    # 获取待审核的帖子（包括AI审核不通过和需要人工审核的）
    pending_posts = Post.query.options(Treet_IP_Conn.joinedload(Post.author)).filter(
        Post.Status == 'pending'
    ).order_by(Post.CreationTime.desc()).all()
    
    # 获取待审核的评论
    pending_comments = Comment.query.options(
        Treet_IP_Conn.joinedload(Comment.author),
        Treet_IP_Conn.joinedload(Comment.post)
    ).filter(Comment.Status == 'pending').order_by(Comment.CreationTime.desc()).all()
    
    return render_template('forum/moderation.html', title='内容审核', pending_posts=pending_posts, pending_comments=pending_comments)

@forum.route('/forum/post/<int:post_id>/approve', methods=['POST'])
@user_required
def approve_post(post_id):
    """批准帖子"""
    if not current_user.is_admin():
        flash('你没有权限执行此操作', 'danger')
        return redirect(url_for('forum.forum_index'))
    
    post = Post.query.get_or_404(post_id)
    post.approve(current_user)
    
    try:
        Treet_IP_Conn.session.commit()
        flash('帖子已批准', 'success')
        clear_cache_for_post(post_id)
    except Exception as e:
        Treet_IP_Conn.session.rollback()
        flash(f'批准失败: {str(e)}', 'danger')
    
    return redirect(url_for('forum.moderation'))

@forum.route('/forum/post/<int:post_id>/reject', methods=['POST'])
@user_required
def reject_post(post_id):
    """拒绝帖子"""
    if not current_user.is_admin():
        flash('你没有权限执行此操作', 'danger')
        return redirect(url_for('forum.forum_index'))
    
    post = Post.query.get_or_404(post_id)
    comment = request.form.get('review_comment', '')
    post.reject(current_user, comment)
    
    try:
        Treet_IP_Conn.session.commit()
        flash('帖子已拒绝', 'success')
        clear_cache_for_post(post_id)
    except Exception as e:
        Treet_IP_Conn.session.rollback()
        flash(f'拒绝失败: {str(e)}', 'danger')
    
    return redirect(url_for('forum.moderation'))

@forum.route('/forum/comment/<int:comment_id>/approve', methods=['POST'])
@user_required
def approve_comment(comment_id):
    """批准评论"""
    if not current_user.is_admin():
        flash('你没有权限执行此操作', 'danger')
        return redirect(url_for('forum.forum_index'))
    
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.PostID
    
    # 批准评论
    comment.Status = 'approved'
    comment.AuditUserID = current_user.UserID
    comment.AuditTime = datetime.utcnow()
    
    try:
        Treet_IP_Conn.session.commit()
        flash('评论已批准', 'success')
        clear_cache_for_post(post_id)
    except Exception as e:
        Treet_IP_Conn.session.rollback()
        flash(f'批准失败: {str(e)}', 'danger')
    
    return redirect(url_for('forum.moderation'))

@forum.route('/forum/comment/<int:comment_id>/reject', methods=['POST'])
@user_required
def reject_comment(comment_id):
    """拒绝评论"""
    if not current_user.is_admin():
        flash('你没有权限执行此操作', 'danger')
        return redirect(url_for('forum.forum_index'))
    
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.PostID
    review_comment = request.form.get('review_comment', '')
    
    # 拒绝评论
    comment.Status = 'rejected'
    comment.ReviewComment = review_comment
    comment.AuditUserID = current_user.UserID
    comment.AuditTime = datetime.utcnow()
    
    try:
        Treet_IP_Conn.session.commit()
        flash('评论已拒绝', 'success')
        clear_cache_for_post(post_id)
    except Exception as e:
        Treet_IP_Conn.session.rollback()
        flash(f'拒绝失败: {str(e)}', 'danger')
    
    return redirect(url_for('forum.moderation'))

@forum.route('/forum/post/<int:post_id>/toggle_sticky', methods=['POST'])
@user_required
def toggle_sticky(post_id):
    """切换帖子置顶状态"""
    if not current_user.is_admin():
        flash('你没有权限执行此操作', 'danger')
        return redirect(url_for('forum.forum_index'))
    
    post = Post.query.get_or_404(post_id)
    post.toggle_sticky()
    
    try:
        Treet_IP_Conn.session.commit()
        flash('帖子置顶状态已更新', 'success')
        clear_cache_for_post(post_id)
    except Exception as e:
        Treet_IP_Conn.session.rollback()
        flash(f'操作失败: {str(e)}', 'danger')
    
    return redirect(url_for('forum.post_detail', post_id=post_id))





# 缓存清除辅助函数
def clear_cache_for_post(post_id):
    """清除与特定帖子相关的所有缓存"""
    cache.delete(f'post_detail_{post_id}')
    cache.clear()  # 清除首页缓存

@forum.route('/forum/category/<int:category_id>')
def category_posts(category_id):
    """分类帖子列表"""
    # 获取分类
    category = Category.query.get_or_404(category_id)
    
    # 获取参数
    sort_by = request.args.get('sort', 'latest')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 构建查询 - 使用多对多关系过滤特定分类的帖子
    query = Post.query.options(Treet_IP_Conn.joinedload(Post.author)).filter(Post.categories.any(Category.CategoryID == category_id), Post.Status == 'approved')
    
    # 排序
    if sort_by == 'latest':
        query = query.order_by(Post.CreationTime.desc())
    elif sort_by == 'hottest':
        # 使用子查询计算每个帖子的评论数并排序
        from sqlalchemy.sql import func
        # 子查询获取每个帖子的评论计数
        comment_count_subquery = Treet_IP_Conn.session.query(
            Comment.PostID,
            func.count(Comment.CommentID).label('comment_count')
        ).group_by(Comment.PostID).subquery()
        # 连接子查询并按评论数排序
        query = query.outerjoin(
            comment_count_subquery,
            Post.PostID == comment_count_subquery.c.PostID
        ).order_by(func.coalesce(comment_count_subquery.c.comment_count, 0).desc())
    elif sort_by == 'most_viewed':
        query = query.order_by(Post.ViewCount.desc())
    
    # 分页
    posts = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 获取所有分类
    categories = Category.query.all()
    
    # 获取热门标签
    tags = Tag.query.order_by(desc(Tag.UsageCount)).limit(10).all()
    
    return render_template('forum/category_posts.html', 
                           category=category, 
                           posts=posts, 
                           categories=categories, 
                           tags=tags, 
                           sort_by=sort_by)

@forum.route('/forum/tag/<int:tag_id>')
def tag_posts(tag_id):
    """标签帖子列表"""
    # 获取标签
    tag = Tag.query.get_or_404(tag_id)
    
    # 获取参数
    sort_by = request.args.get('sort', 'latest')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 构建查询
    query = Post.query.options(Treet_IP_Conn.joinedload(Post.author)).join(Post.tags).filter(Tag.TagID == tag_id, Post.Status == 'approved')
    
    # 排序
    if sort_by == 'latest':
        query = query.order_by(Post.CreationTime.desc())
    elif sort_by == 'hottest':
        query = query.order_by(Post.CommentCount.desc())
    elif sort_by == 'most_viewed':
        query = query.order_by(Post.ViewCount.desc())
    
    # 分页
    posts = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 获取所有分类
    categories = Category.query.all()
    
    # 获取热门标签
    tags = Tag.query.order_by(desc(Tag.UsageCount)).limit(10).all()
    
    return render_template('forum/tag_posts.html', 
                           tag=tag, 
                           posts=posts, 
                           categories=categories, 
                           tags=tags, 
                           sort_by=sort_by)

@forum.route('/forum/search')
def search_page():
    """独立的搜索页面"""
    # 获取搜索参数
    search_query = request.args.get('search', '').strip()
    category_id = request.args.get('category', type=int)
    tag_id = request.args.get('tag', type=int)
    sort_by = request.args.get('sort', 'latest')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 构建查询
    query = Post.query.options(Treet_IP_Conn.joinedload(Post.author)).filter(Post.Status.in_(['approved', 'active']))
    
    # 搜索筛选
    if search_query:
        search_pattern = f'%{search_query}%'
        query = query.filter(
            (Post.PostTitle.like(search_pattern)) |
            (Post.PostContent.like(search_pattern))
        )
    
    # 分类筛选
    if category_id:
        query = query.join(Post.categories).filter(Category.CategoryID == category_id)
    
    # 标签筛选
    if tag_id:
        query = query.join(Post.tags).filter(Tag.TagID == tag_id)
    
    # 排序
    if sort_by == 'latest':
        query = query.order_by(Post.CreationTime.desc())
    elif sort_by == 'popular':
        query = query.order_by(Post.ViewCount.desc())
    elif sort_by == 'comments':
        # 使用子查询计算每个帖子的评论数并排序
        comment_count_subquery = Treet_IP_Conn.session.query(
            Comment.PostID,
            func.count(Comment.CommentID).label('comment_count')
        ).group_by(Comment.PostID).subquery()
        query = query.outerjoin(
            comment_count_subquery,
            Post.PostID == comment_count_subquery.c.PostID
        ).order_by(func.coalesce(comment_count_subquery.c.comment_count, 0).desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items
    
    # 获取分类列表
    categories = Category.query.all()
    
    # 获取热门标签
    popular_tags = Tag.query.order_by(desc(Tag.UsageCount)).limit(20).all()
    
    # 获取选中的分类和标签
    selected_category = Category.query.get(category_id) if category_id else None
    selected_tag = Tag.query.get(tag_id) if tag_id else None
    
    return render_template('forum/search.html', 
                           title='搜索结果', 
                           posts=posts, 
                           pagination=pagination,
                           search_query=search_query,
                           categories=categories,
                           selected_category=selected_category,
                           selected_category_id=category_id,
                           tags=popular_tags,
                           selected_tag=selected_tag,
                           selected_tag_id=tag_id,
                           sort_by=sort_by)

@forum.route('/forum/post/<int:post_id>/edit', methods=['GET', 'POST'])
@user_required
def edit_post(post_id):
    """编辑帖子"""
    # 获取帖子
    post = Post.query.get_or_404(post_id)
    
    # 检查权限
    if post.UserID != current_user.UserID and not current_user.is_admin():
        flash('你没有权限编辑此帖子', 'danger')
        return redirect(url_for('forum.post_detail', post_id=post_id))
    
    # 创建表单
    form = PostForm()
    
    # 手动设置表单字段的值
    form.title.data = post.PostTitle
    form.content.data = post.PostContent
    
    # 设置分类
    if post.categories:
        form.category.data = post.categories[0].CategoryID
    
    # 设置标签
    form.tags.data = ', '.join(tag.TagName for tag in post.tags)
    
    # 处理表单提交
    print(f"请求方法: {request.method}, 表单验证状态: {form.validate_on_submit()}")
    print(f"表单数据: {request.form if request.method == 'POST' else 'N/A'}")
    print(f"表单错误: {form.errors}")
    
    if form.validate_on_submit():
        # 进行AI内容审核
        post_content = form.title.data + "\n" + form.content.data
        is_approved = ai_content_check(post_content)
        
        print(f"AI审核结果: {is_approved}")
        
        # 更新帖子信息，无论审核结果如何
        print(f"更新前标题: {post.PostTitle}, 更新后标题: {form.title.data}")
        print(f"更新前内容: {post.PostContent[:50]}..., 更新后内容: {form.content.data[:50]}...")
        print(f"更新前状态: {post.Status}")
        
        try:
            # 更新帖子基本信息 - 统一使用ORM对象更新方式
            post.PostTitle = form.title.data
            post.PostContent = form.content.data
            post.LastModified = datetime.utcnow()
            post.AIAuditResult = is_approved
            post.AIAuditTime = datetime.utcnow()
            post.IsAIAudit = True
            
            # 关键修复：已通过审核的帖子更新后状态改为待审核
            post.Status = 'pending'
            print(f"更新后状态设置为: {post.Status}")
            
            # 处理分类
            post.categories.clear()
            if form.category.data and form.category.data > 0:
                category = Category.query.get(form.category.data)
                if category:
                    post.categories.append(category)
                    print(f"添加分类: {category.CategoryName}")
        
            # 更新标签
            # 先清除现有标签关联
            post.tags.clear()
            
            # 添加新标签
            if form.tags.data:
                tag_names = [tag.strip() for tag in form.tags.data.split(',')]
                for tag_name in tag_names:
                    if tag_name:
                        # 查找或创建标签
                        tag = Tag.query.filter_by(TagName=tag_name).first()
                        if not tag:
                            tag = Tag(TagName=tag_name, UsageCount=1)
                            Treet_IP_Conn.session.add(tag)
                            print(f"创建新标签: {tag_name}")
                        else:
                            tag.UsageCount += 1
                            print(f"更新标签使用次数: {tag_name}")
                        
                        # 添加帖子-标签关联
                        post.tags.append(tag)
        
            print(f"准备提交事务")
            Treet_IP_Conn.session.commit()
            print(f"事务提交成功")
            
            # 验证更新是否成功
            updated_post = Post.query.get(post_id)
            print(f"更新后数据库中的标题: {updated_post.PostTitle}")
            print(f"更新后数据库中的内容: {updated_post.PostContent[:50]}...")
            print(f"更新后数据库中的状态: {updated_post.Status}")
            
            # 显示更新成功提示
            flash('帖子更新成功，已重新提交审核', 'success')
            
            # 清除缓存
            clear_cache_for_post(post_id)
            print(f"缓存已清除，重定向到帖子详情页")
            return redirect(url_for('forum.post_detail', post_id=post_id))
        except Exception as e:
            Treet_IP_Conn.session.rollback()
            print(f"事务提交失败: {str(e)}")
            flash(f'更新失败: {str(e)}', 'danger')
    else:
        # 预填充标签字段
        if post.tags:
            form.tags.data = ', '.join(tag.TagName for tag in post.tags)
    
    return render_template('forum/edit_post.html', form=form, post=post)

@forum.route('/forum/post/<int:post_id>/delete', methods=['POST'])
@user_required
def delete_post(post_id):
    """删除帖子"""
    # 获取帖子
    post = Post.query.get_or_404(post_id)
    
    # 检查权限 - 作者和管理员可以删除帖子
    if post.UserID != current_user.UserID and not current_user.is_admin():
        flash('没有权限删除此帖子', 'danger')
        return redirect(url_for('forum.post_detail', post_id=post_id))
    
    try:
        # 删除帖子
        Treet_IP_Conn.session.delete(post)
        Treet_IP_Conn.session.commit()
        flash('帖子已成功删除', 'success')
        # 清除缓存
        clear_cache_for_post(post_id)
        return redirect(url_for('forum.forum_index'))
    except Exception as e:
        Treet_IP_Conn.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')
        return redirect(url_for('forum.post_detail', post_id=post_id))

@forum.route('/forum/post/<int:post_id>/resubmit', methods=['POST'])
@user_required
def resubmit_post(post_id):
    """重新提交帖子"""
    post = Post.query.get_or_404(post_id)
    
    # 检查权限
    if post.UserID != current_user.UserID:
        flash('你没有权限执行此操作', 'danger')
        return redirect(url_for('forum.forum_index'))
    
    # 只有被拒绝的帖子才能重新提交
    if post.Status != 'rejected':
        flash('只有被拒绝的帖子才能重新提交', 'danger')
        return redirect(url_for('forum.post_detail', post_id=post_id))
    
    post.resubmit()
    
    try:
        Treet_IP_Conn.session.commit()
        flash('帖子已重新提交，等待管理员审核', 'success')
        clear_cache_for_post(post_id)
    except Exception as e:
        Treet_IP_Conn.session.rollback()
        flash(f'重新提交失败: {str(e)}', 'danger')
    
    return redirect(url_for('forum.post_detail', post_id=post_id))

@forum.route('/forum/comment/<int:comment_id>/delete', methods=['POST'])
@user_required
def delete_comment(comment_id):
    """删除评论"""
    # 获取评论
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.PostID
    
    # 检查权限
    if comment.UserID != current_user.UserID and not current_user.is_admin():
        flash('没有权限删除此评论', 'danger')
        return redirect(url_for('forum.post_detail', post_id=post_id))
    
    try:
        # 删除评论
        Treet_IP_Conn.session.delete(comment)
        Treet_IP_Conn.session.commit()
        flash('评论已成功删除', 'success')
        # 清除缓存
        clear_cache_for_post(post_id)
    except Exception as e:
        Treet_IP_Conn.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')
    
    return redirect(url_for('forum.post_detail', post_id=post_id))