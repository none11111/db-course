#!/usr/bin/env python3
"""
论坛内容重置脚本
功能：
1. 删除所有现有帖子和评论
2. 生成新的扶贫助农、种植经验、土地治理主题的内容
3. 确保所有内容都处于已批准状态，能在首页正常显示
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import Treet_IP_Conn, Post, Comment
from app.utils.db_utils import init_test_data


def reset_forum_content():
    """重置论坛内容"""
    app = create_app('development')
    
    with app.app_context():
        try:
            print("开始重置论坛内容...")
            
            # 删除所有评论
            comment_count = Comment.query.count()
            if comment_count > 0:
                Comment.query.delete()
                Treet_IP_Conn.session.commit()
                print(f"已删除 {comment_count} 条评论")
            else:
                print("没有找到评论数据")
            
            # 删除所有帖子
            post_count = Post.query.count()
            if post_count > 0:
                Post.query.delete()
                Treet_IP_Conn.session.commit()
                print(f"已删除 {post_count} 个帖子")
            else:
                print("没有找到帖子数据")
            
            # 生成新的测试数据
            print("\n生成新的论坛内容...")
            init_test_data()
            
            print("\n论坛内容重置完成！")
            print("新内容已生成，包含扶贫助农、种植经验、土地治理等主题")
            print("所有内容都已设置为已批准状态，可以在论坛首页正常显示")
            
        except Exception as e:
            print(f"重置过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True


if __name__ == '__main__':
    reset_forum_content()