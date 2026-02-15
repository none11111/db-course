#!/usr/bin/env python3
"""
论坛诊断脚本
功能：
1. 检查数据库连接
2. 验证帖子和评论表结构
3. 测试论坛统计功能
4. 检查是否有已批准的帖子
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_database_connection():
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    try:
        from app import create_app
        app = create_app('development')
        
        with app.app_context():
            from app import db
            result = db.session.execute('SELECT 1')
            print("✓ 数据库连接成功")
            return True
            
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_table_structures():
    """测试表结构"""
    print("\n=== 测试表结构 ===")
    try:
        from app import create_app
        app = create_app('development')
        
        with app.app_context():
            from app import db
            from sqlalchemy import inspect
            
            # 获取数据库检查器
            inspector = inspect(db.engine)
            
            # 检查Posts表
            print("检查Posts表...")
            post_columns = inspector.get_columns('Posts')
            post_column_names = [col['name'] for col in post_columns]
            
            required_columns = ['PostID', 'PostTitle', 'PostContent', 'UserID', 'CreationTime', 'Status', 'AIAuditResult', 'AIAuditTime', 'IsAIAudit']
            
            for col in required_columns:
                if col in post_column_names:
                    print(f"  ✓ {col} - 存在")
                else:
                    print(f"  ✗ {col} - 缺失")
            
            # 检查Comments表
            print("\n检查Comments表...")
            comment_columns = inspector.get_columns('Comments')
            comment_column_names = [col['name'] for col in comment_columns]
            
            required_comment_columns = ['CommentID', 'PostID', 'CommentContent', 'UserID', 'CreationTime', 'Status', 'AIAuditResult', 'AIAuditTime', 'IsAIAudit']
            
            for col in required_comment_columns:
                if col in comment_column_names:
                    print(f"  ✓ {col} - 存在")
                else:
                    print(f"  ✗ {col} - 缺失")
            
            return True
            
    except Exception as e:
        print(f"✗ 表结构检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_forum_statistics():
    """测试论坛统计功能"""
    print("\n=== 测试论坛统计功能 ===")
    try:
        from app import create_app
        app = create_app('development')
        
        with app.app_context():
            from app.utils.db_utils import get_forum_statistics
            
            stats = get_forum_statistics()
            print("✓ 论坛统计功能正常")
            print(f"统计数据：")
            print(f"- 活跃用户数: {stats['user_count']}")
            print(f"- 总帖子数: {stats['post_count']}")
            print(f"- 总评论数: {stats['comment_count']}")
            print(f"- 今日新增帖子数: {stats['today_post_count']}")
            
            return True
            
    except Exception as e:
        print(f"✗ 论坛统计功能失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_posts_exist():
    """测试是否有已批准的帖子"""
    print("\n=== 测试是否有已批准的帖子 ===")
    try:
        from app import create_app
        app = create_app('development')
        
        with app.app_context():
            from app.models import Post
            
            # 获取已批准的帖子
            approved_posts = Post.query.filter(Post.Status.in_(['approved', 'active'])).all()
            print(f"✓ 已批准的帖子数: {len(approved_posts)}")
            
            # 打印前5个帖子标题
            if approved_posts:
                print("前5个已批准的帖子：")
                for i, post in enumerate(approved_posts[:5]):
                    print(f"  {i+1}. {post.PostTitle} (状态: {post.Status})")
            else:
                print("✗ 没有找到已批准的帖子，这可能是首页看不到内容的原因")
            
            return True
            
    except Exception as e:
        print(f"✗ 帖子查询失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("    扶贫助农论坛 - 诊断工具")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        test_database_connection,
        test_table_structures,
        test_forum_statistics,
        test_posts_exist
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ 测试 {test.__name__} 执行错误: {e}")
            failed += 1
    
    # 打印测试结果
    print("\n" + "=" * 60)
    print(f"诊断结果: 通过 {passed} 个, 失败 {failed} 个")
    print("=" * 60)
    
    if failed == 0:
        print("✓ 所有测试通过！论坛功能正常。")
    else:
        print("✗ 部分测试失败，论坛可能存在问题。")
        print("请根据上面的错误信息排查问题，或联系技术支持。")
    
    return failed


if __name__ == '__main__':
    sys.exit(main())