from app import create_app
from app.models import Comment, Post

app = create_app('development')
with app.app_context():
    # 查询所有评论及其状态
    comments = Comment.query.all()
    print(f'总评论数: {len(comments)}')
    
    # 按状态分组统计
    status_counts = {}
    for comment in comments:
        status = comment.Status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print('\n评论状态统计:')
    for status, count in status_counts.items():
        print(f'  {status}: {count}')
    
    # 显示前10条评论的详细信息
    print('\n前10条评论详情:')
    for i, comment in enumerate(comments[:10]):
        post = Post.query.get(comment.PostID)
        post_title = post.PostTitle if post else "N/A"
        print(f'{i+1}. 评论ID: {comment.CommentID}, 状态: {comment.Status}, 帖子: {post_title}')
        print(f'   内容: {comment.CommentContent[:50]}...')