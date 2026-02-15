from app import create_app, Treet_IP_Conn
from app.models.user import User
from sqlalchemy import text

app = create_app('development')

with app.app_context():
    try:
        # 检查并添加积分相关字段
        inspector = Treet_IP_Conn.inspect(Treet_IP_Conn.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        print(f"当前users表的列: {columns}")
        
        # 添加积分字段
        if 'Points' not in columns:
            Treet_IP_Conn.session.execute(text('ALTER TABLE users ADD COLUMN Points INTEGER DEFAULT 0'))
            print("添加字段: Points")
        
        if 'Level' not in columns:
            Treet_IP_Conn.session.execute(text('ALTER TABLE users ADD COLUMN Level INTEGER DEFAULT 1'))
            print("添加字段: Level")
        
        if 'TotalPointsEarned' not in columns:
            Treet_IP_Conn.session.execute(text('ALTER TABLE users ADD COLUMN TotalPointsEarned INTEGER DEFAULT 0'))
            print("添加字段: TotalPointsEarned")
        
        if 'ConsecutiveCheckInDays' not in columns:
            Treet_IP_Conn.session.execute(text('ALTER TABLE users ADD COLUMN ConsecutiveCheckInDays INTEGER DEFAULT 0'))
            print("添加字段: ConsecutiveCheckInDays")
        
        if 'LastCheckInDate' not in columns:
            Treet_IP_Conn.session.execute(text('ALTER TABLE users ADD COLUMN LastCheckInDate DATE'))
            print("添加字段: LastCheckInDate")
        
        if 'IsPhoneBound' not in columns:
            Treet_IP_Conn.session.execute(text('ALTER TABLE users ADD COLUMN IsPhoneBound BOOLEAN DEFAULT 0'))
            print("添加字段: IsPhoneBound")
        
        if 'IsEmailBound' not in columns:
            Treet_IP_Conn.session.execute(text('ALTER TABLE users ADD COLUMN IsEmailBound BOOLEAN DEFAULT 0'))
            print("添加字段: IsEmailBound")
        
        if 'IsProfileCompleted' not in columns:
            Treet_IP_Conn.session.execute(text('ALTER TABLE users ADD COLUMN IsProfileCompleted BOOLEAN DEFAULT 0'))
            print("添加字段: IsProfileCompleted")
        
        # 提交事务
        Treet_IP_Conn.session.commit()
        
        # 创建积分相关表
        Treet_IP_Conn.create_all()
        print("数据库表创建完成")
        
        print("\n数据库迁移成功完成！")
        
    except Exception as e:
        Treet_IP_Conn.session.rollback()
        print(f"数据库迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
