from app import create_app
from app.models import Post
from app import Treet_IP_Conn

app = create_app('development')
with app.app_context():
    posts = Post.query.all()
    print(f'数据库中共有 {len(posts)} 个帖子')
    print('\n帖子列表：')
    for post in posts:
        print(f'ID: {post.PostID}, 标题: {post.PostTitle}, 状态: {post.Status}, AI审核结果: {post.AIAuditResult}')
