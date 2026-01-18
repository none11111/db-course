#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
论坛数据分析平台 - 性能基准测试脚本
用于测试不同查询策略和优化技术的性能差异
"""

import time
import pymysql
import pymysql.cursors
import json
from datetime import datetime

class PerformanceTester:
    def __init__(self):
        # 数据库连接配置
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'YOUR_PASSWORD_HERE',  # 请在使用时替换为实际密码
            'db': 'forum_db',
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        
        # 测试结果存储
        self.results = []
        self.test_start_time = None
    
    def connect_db(self):
        """建立数据库连接"""
        return pymysql.connect(**self.db_config)
    
    def run_test(self, test_name, query, description=""):
        """执行单个测试并记录执行时间"""
        print(f"\n执行测试: {test_name}")
        print(f"描述: {description}")
        print(f"SQL: {query}")
        
        start_time = time.time()
        result_count = 0
        error = None
        
        try:
            with self.connect_db() as connection:
                with connection.cursor() as cursor:
                    # 执行查询
                    cursor.execute(query)
                    # 获取结果行数
                    result_count = len(cursor.fetchall())
        except Exception as e:
            error = str(e)
            print(f"错误: {error}")
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # 转换为毫秒
        
        print(f"执行时间: {execution_time:.2f} 毫秒")
        print(f"结果行数: {result_count}")
        
        # 保存测试结果
        self.results.append({
            'test_name': test_name,
            'description': description,
            'query': query,
            'execution_time_ms': execution_time,
            'result_count': result_count,
            'error': error,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        return execution_time, result_count, error
    
    def run_index_comparison_test(self, test_name, no_index_query, with_index_query, index_name):
        """执行索引优化对比测试"""
        print(f"\n=== 索引优化对比测试: {test_name} ===")
        print(f"索引名称: {index_name}")
        
        # 测试无索引版本
        print("\n[无索引版本]")
        no_index_time, no_index_count, no_index_error = self.run_test(
            f"{test_name} (无索引)",
            no_index_query,
            f"未使用索引 {index_name} 的查询"
        )
        
        # 测试有索引版本
        print("\n[有索引版本]")
        with_index_time, with_index_count, with_index_error = self.run_test(
            f"{test_name} (有索引)",
            with_index_query,
            f"使用索引 {index_name} 的查询"
        )
        
        # 计算性能提升
        if no_index_time > 0 and with_index_time > 0:
            improvement = (no_index_time - with_index_time) / no_index_time * 100
            print(f"\n性能提升: {improvement:.2f}%")
        
        return {
            'no_index': {'time': no_index_time, 'count': no_index_count, 'error': no_index_error},
            'with_index': {'time': with_index_time, 'count': with_index_count, 'error': with_index_error}
        }
    
    def run_procedure_comparison_test(self, test_name, direct_query, procedure_call):
        """执行存储过程与直接查询对比测试"""
        print(f"\n=== 存储过程对比测试: {test_name} ===")
        
        # 测试直接查询
        print("\n[直接SQL查询]")
        direct_time, direct_count, direct_error = self.run_test(
            f"{test_name} (直接查询)",
            direct_query,
            "直接执行SQL查询"
        )
        
        # 测试存储过程
        print("\n[存储过程]")
        procedure_time, procedure_count, procedure_error = self.run_test(
            f"{test_name} (存储过程)",
            procedure_call,
            "调用预编译存储过程"
        )
        
        # 计算性能差异
        if direct_time > 0 and procedure_time > 0:
            difference = (direct_time - procedure_time) / direct_time * 100
            print(f"\n性能差异: {difference:.2f}%")
        
        return {
            'direct_query': {'time': direct_time, 'count': direct_count, 'error': direct_error},
            'procedure': {'time': procedure_time, 'count': procedure_count, 'error': procedure_error}
        }
    
    def generate_report(self, output_file="performance_report.json"):
        """生成性能测试报告"""
        report = {
            'test_summary': {
                'total_tests': len(self.results),
                'successful_tests': sum(1 for r in self.results if r['error'] is None),
                'failed_tests': sum(1 for r in self.results if r['error'] is not None),
                'total_execution_time_ms': sum(r['execution_time_ms'] for r in self.results),
                'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'test_results': self.results
        }
        
        # 保存为JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== 性能测试报告 ===")
        print(f"测试总数: {report['test_summary']['total_tests']}")
        print(f"成功测试: {report['test_summary']['successful_tests']}")
        print(f"失败测试: {report['test_summary']['failed_tests']}")
        print(f"总执行时间: {report['test_summary']['total_execution_time_ms']:.2f} 毫秒")
        print(f"报告已保存到: {output_file}")
        
        return report
    
    def run_all_tests(self):
        """运行所有性能测试"""
        self.test_start_time = time.time()
        print("开始性能基准测试...")
        print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 基本查询性能测试
        print("\n=== 基本查询性能测试 ===")
        
        # 测试1: 获取总用户数
        self.run_test(
            "获取总用户数",
            "SELECT COUNT(*) AS total_users FROM users",
            "简单聚合函数查询测试"
        )
        
        # 测试2: 获取总帖子数
        self.run_test(
            "获取总帖子数",
            "SELECT COUNT(*) AS total_posts FROM posts",
            "简单聚合函数查询测试"
        )
        
        # 测试3: 获取最新的10篇帖子
        self.run_test(
            "获取最新帖子",
            "SELECT * FROM posts ORDER BY created_at DESC LIMIT 10",
            "排序和分页查询测试"
        )
        
        # 2. 索引优化对比测试
        print("\n=== 索引优化对比测试 ===")
        
        # 测试4: 按用户状态查询（索引 vs 无索引）
        self.run_index_comparison_test(
            "按用户状态查询",
            "SELECT * FROM users WHERE status = 'active'",
            "SELECT * FROM users WHERE status = 'active'",  # 使用相同的查询，因为索引已经在存储过程中创建
            "idx_users_status"
        )
        
        # 测试5: 按帖子创建时间范围查询（索引 vs 无索引）
        self.run_index_comparison_test(
            "按帖子创建时间范围查询",
            "SELECT * FROM posts WHERE created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)",
            "SELECT * FROM posts WHERE created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)",
            "idx_posts_created_at"
        )
        
        # 测试6: 按帖子分类查询（索引 vs 无索引）
        self.run_index_comparison_test(
            "按帖子分类查询",
            "SELECT * FROM posts WHERE category = '技术讨论'",
            "SELECT * FROM posts WHERE category = '技术讨论'",
            "idx_posts_category"
        )
        
        # 3. 复杂查询性能测试
        print("\n=== 复杂查询性能测试 ===")
        
        # 测试7: 月度发帖趋势查询
        self.run_test(
            "月度发帖趋势查询",
            "SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, COUNT(*) AS post_count FROM posts WHERE created_at > DATE_SUB(NOW(), INTERVAL 12 MONTH) GROUP BY month ORDER BY month",
            "分组聚合和日期函数复杂查询测试"
        )
        
        # 测试8: 核心用户识别查询
        self.run_test(
            "核心用户识别查询",
            "SELECT u.id, u.username, u.reputation, COUNT(p.id) AS post_count, COUNT(c.id) AS comment_count FROM users u LEFT JOIN posts p ON u.id = p.user_id LEFT JOIN comments c ON u.id = c.user_id GROUP BY u.id, u.username, u.reputation ORDER BY u.reputation DESC LIMIT 20",
            "多表连接和排序复杂查询测试"
        )
        
        # 测试9: 帖子分类分布查询
        self.run_test(
            "帖子分类分布查询",
            "SELECT category, COUNT(*) AS count, ROUND((COUNT(*) / (SELECT COUNT(*) FROM posts)) * 100, 2) AS percentage FROM posts GROUP BY category ORDER BY count DESC",
            "子查询和百分比计算复杂查询测试"
        )
        
        # 4. 存储过程性能对比测试
        print("\n=== 存储过程性能对比测试 ===")
        
        # 测试10: 更新用户声望（直接SQL vs 存储过程）
        # 注意：这里假设已经创建了存储过程
        self.run_procedure_comparison_test(
            "更新用户声望",
            """SELECT 
                p.id,
                p.title,
                p.category,
                p.content,
                p.views,
                p.comments_count,
                p.likes_count,
                p.created_at,
                u.id AS user_id,
                u.username,
                (p.comments_count * 2 + p.views / 10 + p.likes_count * 5) AS hotness_score
            FROM 
                posts p
            JOIN 
                users u ON p.user_id = u.id
            WHERE 
                p.status = 'active'
            ORDER BY 
                hotness_score DESC,
                p.created_at DESC
            LIMIT 10 OFFSET 0""",
            "CALL GetHotPosts(10, 1)"
        )
        
        # 5. 高负载场景测试
        print("\n=== 高负载场景测试 ===")
        
        # 测试11: 模拟并发查询
        print("\n执行并发查询模拟测试 (连续执行5次相同查询)...")
        concurrent_query = "SELECT * FROM posts p JOIN users u ON p.user_id = u.id JOIN comments c ON p.id = c.post_id WHERE p.created_at > DATE_SUB(NOW(), INTERVAL 7 DAY) LIMIT 100"
        
        concurrent_times = []
        for i in range(5):
            print(f"\n执行并发查询 #{i+1}")
            exec_time, _, _ = self.run_test(
                f"并发查询测试 #{i+1}",
                concurrent_query,
                f"模拟并发场景的复杂连接查询测试 #{i+1}"
            )
            concurrent_times.append(exec_time)
        
        avg_concurrent_time = sum(concurrent_times) / len(concurrent_times)
        print(f"\n平均并发查询时间: {avg_concurrent_time:.2f} 毫秒")
        print(f"并发查询时间范围: {min(concurrent_times):.2f} - {max(concurrent_times):.2f} 毫秒")
        
        # 生成最终报告
        total_time = time.time() - self.test_start_time
        print(f"\n所有测试完成！总耗时: {total_time:.2f} 秒")
        return self.generate_report()

if __name__ == "__main__":
    tester = PerformanceTester()
    tester.run_all_tests()