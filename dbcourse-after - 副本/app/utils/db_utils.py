"""数据库统计工具模块"""
from datetime import date, datetime, timedelta
from sqlalchemy import func
from ..models import Treet_IP_Conn, User, Post, Comment, Category, Tag
import random
import string


def get_forum_statistics():
    """
    获取论坛统计数据
    :return: 包含各种统计信息的字典
    """
    try:
        # 总用户数（所有用户，因为Status字段可能不一致）
        user_count = User.query.count()
        
        # 总帖子数（只统计已批准的帖子）
        post_count = Post.query.filter(Post.Status.in_(['approved', 'active'])).count()
        
        # 总评论数（只统计已批准的评论）
        comment_count = Comment.query.filter(Comment.Status.in_(['approved', 'active'])).count()
        
        # 今日新增帖子数（只统计已批准的帖子）
        today = date.today()
        today_post_count = Post.query.filter(
            func.date(Post.CreationTime) == today,
            Post.Status.in_(['approved', 'active'])
        ).count()
        
        # 本周新增帖子数
        one_week_ago = today - timedelta(days=7)
        week_post_count = Post.query.filter(
            Post.CreationTime >= one_week_ago
        ).count()
        
        # 本月新增帖子数
        one_month_ago = today - timedelta(days=30)
        month_post_count = Post.query.filter(
            Post.CreationTime >= one_month_ago
        ).count()
        
        # 分类统计
        category_stats = []
        categories = Category.query.all()
        for category in categories:
            category_posts = Post.query.filter(
                Post.categories.any(Category.CategoryID == category.CategoryID)
            ).count()
            category_stats.append({
                'name': category.CategoryName,
                'count': category_posts
            })
        
        # 热门标签（使用次数最多的前10个）
        popular_tags = Tag.query.order_by(Tag.UsageCount.desc()).limit(10).all()
        popular_tags_stats = [{
            'name': tag.TagName,
            'count': tag.UsageCount
        } for tag in popular_tags]
        
        return {
            'user_count': user_count,
            'post_count': post_count,
            'comment_count': comment_count,
            'today_post_count': today_post_count,
            'week_post_count': week_post_count,
            'month_post_count': month_post_count,
            'category_stats': category_stats,
            'popular_tags': popular_tags_stats
        }
    except Exception as e:
        print(f"统计数据查询失败: {e}")
        return {
            'user_count': 0,
            'post_count': 0,
            'comment_count': 0,
            'today_post_count': 0,
            'week_post_count': 0,
            'month_post_count': 0,
            'category_stats': [],
            'popular_tags': []
        }


def get_user_activity(user_id, days=30):
    """
    获取用户活动统计
    :param user_id: 用户ID
    :param days: 统计天数
    :return: 用户活动统计信息
    """
    try:
        start_date = date.today() - timedelta(days=days)
        
        # 用户发布的帖子数
        user_posts = Post.query.filter(
            Post.UserID == user_id,
            Post.CreationTime >= start_date
        ).count()
        
        # 用户发布的评论数
        user_comments = Comment.query.filter(
            Comment.UserID == user_id,
            Comment.CreationTime >= start_date
        ).count()
        
        return {
            'posts': user_posts,
            'comments': user_comments
        }
    except Exception as e:
        print(f"用户活动统计失败: {e}")
        return {'posts': 0, 'comments': 0}


def get_trending_posts(days=7, limit=5):
    """
    获取热门帖子
    :param days: 统计天数
    :param limit: 返回数量
    :return: 热门帖子列表
    """
    try:
        start_date = date.today() - timedelta(days=days)
        
        # 按浏览量排序的热门帖子
        trending_posts = Post.query.filter(
            Post.CreationTime >= start_date
        ).order_by(Post.ViewCount.desc()).limit(limit).all()
        
        return trending_posts
    except Exception as e:
        print(f"热门帖子查询失败: {e}")
        return []

def init_test_data():
    """生成测试数据 - 扶贫助农、种植经验、土地治理主题"""
    try:
        print("开始生成测试数据...")
        
        # 生成用户数据
        categories = ['种植经验', '土地治理', '扶贫政策', '农业技术', '市场资讯', '问题求助']
        tags_list = ['水稻种植', '蔬菜栽培', '土壤改良', '生态治理', '精准扶贫', '农业机械化', '病虫害防治', '农村电商', '有机农业', '灌溉技术']
        
        # 检查是否已有用户，如果没有则创建20个测试用户
        users = User.query.all()
        if not users:
            users = []
            
            # 创建管理员账号
            admin = User(
                UserName='admin',
                UserEmail='admin@example.com',
                RegistrationDate=datetime.utcnow(),
                Status='ACTIVE',
                Role='ADMIN'  # 设置为管理员角色
            )
            admin.set_password('admin123')  # 管理员密码
            users.append(admin)
            Treet_IP_Conn.session.add(admin)
            print("创建了管理员账号: admin / admin123")
            
            # 创建普通用户
            for i in range(20):
                user = User(
                    UserName=f'农友{i+1}',
                    UserEmail=f'nongyou{i+1}@example.com',  # 添加email字段
                    RegistrationDate=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                    Status='ACTIVE'  # 使用字符串状态值
                )
                user.set_password('123456')  # 统一密码
                users.append(user)
                Treet_IP_Conn.session.add(user)
            
            Treet_IP_Conn.session.commit()
            print(f"创建了 {len(users)} 个用户（包含1个管理员）")
        else:
            # 检查是否已有管理员账号
            admin_exists = User.query.filter_by(Role='ADMIN').first()
            if not admin_exists:
                # 创建管理员账号
                admin = User(
                    UserName='admin',
                    UserEmail='admin@example.com',
                    RegistrationDate=datetime.utcnow(),
                    Status='ACTIVE',
                    Role='ADMIN'  # 设置为管理员角色
                )
                admin.set_password('admin123')  # 管理员密码
                Treet_IP_Conn.session.add(admin)
                Treet_IP_Conn.session.commit()
                users.append(admin)
                print("创建了管理员账号: admin / admin123")
            
            print(f"使用现有 {len(users)} 个用户")
        
        # 导入Category和Tag模型
        from ..models import Category, Tag
        
        # 创建分类和标签
        category_objects = Category.query.all()
        if not category_objects:
            category_objects = []
            for cat_name in categories:
                cat = Category(CategoryName=cat_name, Description=f'{cat_name}分类 - 分享农业相关经验与资讯')
                Treet_IP_Conn.session.add(cat)
                category_objects.append(cat)
            
            Treet_IP_Conn.session.commit()
        
        tag_objects = Tag.query.all()
        if not tag_objects:
            tag_objects = []
            for tag_name in tags_list:
                tag = Tag(TagName=tag_name)
                Treet_IP_Conn.session.add(tag)
                tag_objects.append(tag)
            
            Treet_IP_Conn.session.commit()
        
        # 创建帖子数据
        posts = []
        titles = [
            '水稻高产种植技术分享',
            '如何改良酸性土壤',
            '蔬菜大棚种植管理经验',
            '农村土地流转政策解读',
            '有机蔬菜种植要点',
            '果树病虫害防治方法',
            '农田水利灌溉系统设计',
            '精准扶贫项目申请指南',
            '农业机械使用与维护',
            '农村电商发展路径探讨',
            '生态农业模式案例分析',
            '土壤污染治理技术',
            '特色农产品种植规划',
            '农业合作社运营管理',
            '乡村振兴战略解读'
        ]
        
        post_contents = [
            '1. 选种：选择适合当地气候的优质高产水稻品种...\n2. 育秧：采用旱育秧技术，控制好温度和湿度...\n3. 插秧：合理密植，每亩种植2.5-3万株...\n4. 田间管理：科学施肥，及时防治病虫害...\n5. 收获：在稻谷成熟度达到85%-90%时收获...',
            '酸性土壤改良方法：\n1. 施加生石灰：根据土壤酸化程度，每亩施加50-150公斤生石灰...\n2. 增施有机肥：提高土壤有机质含量，改善土壤结构...\n3. 种植绿肥：如紫云英、苜蓿等，增加土壤氮含量...\n4. 合理施肥：减少生理酸性肥料的使用...',
            '蔬菜大棚管理要点：\n1. 温度控制：白天保持25-30℃，夜间保持15-18℃...\n2. 湿度管理：通过通风、滴灌等方式控制湿度...\n3. 光照管理：及时清理棚膜灰尘，保证光照充足...\n4. 病虫害防治：采用物理防治和生物防治相结合的方法...',
            '土地流转政策要点：\n1. 流转原则：坚持依法、自愿、有偿原则...\n2. 流转期限：最长不得超过承包期的剩余期限...\n3. 流转方式：可以采取转包、出租、互换、转让等方式...\n4. 流转程序：签订书面合同，报发包方备案...',
            '有机蔬菜种植技术：\n1. 基地选择：远离污染源，土壤质量符合有机标准...\n2. 品种选择：选择抗病虫害、适应性强的品种...\n3. 土壤管理：采用轮作、间作等方式提高土壤肥力...\n4. 病虫害防治：使用物理防治、生物防治和有机农药...\n5. 认证管理：按照有机认证要求进行生产和管理...',
            '果树病虫害防治方法：\n1. 农业防治：加强果园管理，合理修剪，清除病残体...\n2. 物理防治：使用诱虫灯、粘虫板等物理方法...\n3. 生物防治：利用天敌、生物农药等控制病虫害...\n4. 化学防治：在必要时使用低毒、低残留农药...',
            '农田水利灌溉系统设计：\n1. 水源选择：优先选择地表水，其次是地下水...\n2. 灌溉方式：根据作物种类选择喷灌、滴灌、微灌等方式...\n3. 管道设计：合理布局管道，减少水头损失...\n4. 控制系统：采用自动化控制系统，提高灌溉效率...',
            '精准扶贫项目申请指南：\n1. 项目选择：结合当地资源优势和市场需求选择项目...\n2. 申请条件：符合当地精准扶贫政策要求...\n3. 申请材料：准备项目计划书、资金预算等材料...\n4. 申请流程：向当地扶贫办提交申请，经过审核、公示等程序...\n5. 项目实施：按照项目计划组织实施，接受监督检查...'
        ]
        
        # 确保至少创建50个帖子
        existing_post_count = Post.query.count()
        posts_to_create = max(0, 50 - existing_post_count)
        
        for i in range(posts_to_create):
            user = random.choice(users)
            title = random.choice(titles)
            if random.random() > 0.5:  # 50%的概率添加编号
                title += f' #{i+1}'
            
            post = Post(
                PostTitle=title,
                PostContent=random.choice(post_contents),
                ViewCount=random.randint(0, 1000),
                UserID=user.UserID,  # 使用正确的字段名
                CreationTime=datetime.utcnow() - timedelta(days=random.randint(1, 180)),
                PublishTime=datetime.utcnow() - timedelta(days=random.randint(0, 180)),
                Status='approved'  # 设置为已批准状态，确保能在首页显示
            )
            # 添加分类（多对多关系）
            category_count = random.randint(1, 2)
            selected_categories = random.sample(category_objects, k=category_count)
            post.categories = selected_categories
            
            # 添加标签（多对多关系）
            tag_count = random.randint(1, 3)
            selected_tags = random.sample(tag_objects, k=tag_count)
            post.tags = selected_tags
            posts.append(post)
            Treet_IP_Conn.session.add(post)
        
        if posts:
            Treet_IP_Conn.session.commit()
            print(f"创建了 {len(posts)} 个帖子")
        else:
            print("已有足够的帖子数据，未创建新帖子")
        
        # 确保所有帖子都有评论
        all_posts = Post.query.all()
        comments_content = [
            '感谢分享！这些经验对我很有帮助',
            '请问这个技术在南方地区适用吗？',
            '我也有类似的经验，补充一点...',
            '学习了，准备尝试一下',
            '可以详细解释一下其中的原理吗？',
            '这个方法成本高吗？',
            '在我们当地好像不太适用，可能需要调整',
            '收藏了，以后慢慢研究',
            '请问哪里可以买到相关的种子/肥料？',
            '有没有成功案例可以分享一下？'
        ]
        
        for post in all_posts:
            # 检查帖子是否已有评论
            existing_comments = Comment.query.filter_by(PostID=post.PostID).count()
            if existing_comments < 2:
                # 为每个帖子生成2-10条评论
                comment_count = random.randint(2, 10)
                for i in range(comment_count):
                    user = random.choice(users)
                    comment = Comment(
                        CommentContent=random.choice(comments_content),
                        UserID=user.UserID,
                        PostID=post.PostID,
                        CreationTime=post.CreationTime + timedelta(days=random.randint(0, 10)),
                        Status='approved'  # 设置为已批准状态
                    )
                    Treet_IP_Conn.session.add(comment)
        
        Treet_IP_Conn.session.commit()
        print("评论数据处理完成")
        
        # 生成一些回复评论
        all_comments = Comment.query.filter_by(ParentCommentID=None).all()
        for comment in all_comments:
            if random.random() > 0.7:  # 30%的概率有回复
                reply_count = random.randint(1, 3)
                for i in range(reply_count):
                    user = random.choice(users)
                    reply = Comment(
                        CommentContent=f"回复: {random.choice(comments_content)}",
                        UserID=user.UserID,
                        PostID=comment.PostID,
                        ParentCommentID=comment.CommentID,
                        CreationTime=comment.CreationTime + timedelta(hours=random.randint(1, 72)),
                        Status='approved'  # 设置为已批准状态
                    )
                    Treet_IP_Conn.session.add(reply)
        
        Treet_IP_Conn.session.commit()
        print("回复评论生成完成！")
        print("测试数据生成完成！")
        
    except Exception as e:
        Treet_IP_Conn.session.rollback()
        print(f"生成测试数据时出错: {e}")
        import traceback
        traceback.print_exc()

def create_stored_procedures():
    """创建存储过程（兼容MySQL语法，移除DELIMITER命令）"""
    try:
        # 导入text函数
        from sqlalchemy import text
        
        # 使用正确的方式执行SQL语句
        with Treet_IP_Conn.engine.connect() as conn:
            # 创建获取热门帖子的视图（SQLite版本）
            get_hot_posts_sql = """
            CREATE VIEW hot_posts AS
            SELECT 
                p.PostID AS PostID,
                p.PostTitle AS Title,
                p.PostContent AS Content,
                p.UserID AS AuthorID,
                u.UserName AS AuthorName,
                p.Status AS Status,
                p.ViewCount AS ViewCount,
                (SELECT COUNT(*) FROM comments WHERE PostID = p.PostID) AS ReplyCount,
                p.CreationTime AS CreationTime
            FROM 
                posts p
            JOIN 
                users u ON p.UserID = u.UserID
            WHERE 
                p.Status = 'approved'
            ORDER BY 
                p.CreationTime DESC
            LIMIT 10;
            """
            
            # SQLite 不支持 CREATE OR REPLACE VIEW，需要先删除再创建
            drop_view_sql = """
            DROP VIEW IF EXISTS hot_posts;
            """
            
            conn.execute(text(drop_view_sql))
            conn.execute(text(get_hot_posts_sql))
            print("视图创建完成")
            
            # 注意：触发器和存储过程的创建需要特殊处理，这里暂时跳过
            # 因为DELIMITER是MySQL客户端命令，不能通过SQLAlchemy执行
            print("跳过触发器和存储过程创建（需通过MySQL客户端手动创建）")
            
    except Exception as e:
        print(f"创建存储过程时出错: {str(e)}")
        import traceback
        traceback.print_exc()