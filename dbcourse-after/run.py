from app import create_app
from app.models import Treet_IP_Conn
from app.utils.db_utils import init_test_data, create_stored_procedures
import webbrowser
import threading

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 在应用上下文中初始化数据库
    with app.app_context():
        try:
            # 只创建表（如果不存在），不删除现有表
            Treet_IP_Conn.create_all()
            print("✓ 数据库表结构已确保创建")
            
            # 确保存储过程已创建（即使失败也继续启动应用）
            print("检查和创建存储过程...")
            try:
                create_stored_procedures()
                print("✓ 存储过程创建完成")
            except Exception as sp_error:
                print(f"! 存储过程创建失败，但应用仍将继续启动: {sp_error}")
            
            print("数据库初始化完成")
        except Exception as e:
            print(f"✗ 数据库初始化失败: {e}")
            import traceback
            traceback.print_exc()
    
    def open_browser():
        """在服务器启动后自动打开浏览器"""
        import time
        # 等待2秒确保服务器已经启动
        time.sleep(2)
        # 打开浏览器访问应用首页
        webbrowser.open_new("http://localhost:5000/")

    # 创建并启动线程
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动应用，关闭自动重载功能以避免打开多个浏览器窗口
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)