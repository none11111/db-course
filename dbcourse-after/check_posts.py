from app import create_app
from app.models import db, Post

# 创建Flask应用实例
app = create_app()

with app.app_context():
    # 查询所有帖子
    all_posts = Post.query.all()
    print(f"总共有 {len(all_posts)} 个帖子")
    
    if all_posts:
        print("\n帖子详情：")
        for post in all_posts:
            print(f"ID: {post.PostID}")
            print(f"标题: {post.PostTitle}")
            print(f"作者ID: {post.UserID}")
            print(f"状态: {post.Status}")
            print(f"创建时间: {post.CreationTime}")
            print("-" * 30)
    
    # 查询待审核帖子
    pending_posts = Post.query.filter_by(Status='pending').all()
    print(f"\n待审核帖子: {len(pending_posts)} 个")
    
    # 查询已批准帖子
    approved_posts = Post.query.filter_by(Status='approved').all()
    print(f"已批准帖子: {len(approved_posts)} 个")
    
    # 查询已拒绝帖子
    rejected_posts = Post.query.filter_by(Status='rejected').all()
    print(f"已拒绝帖子: {len(rejected_posts)} 个")