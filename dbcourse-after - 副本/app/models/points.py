from . import Treet_IP_Conn
from datetime import datetime
import enum

class PointActionType(enum.Enum):
    """积分操作类型枚举"""
    # 基础行为
    DAILY_CHECK_IN = 'DAILY_CHECK_IN'  # 每日签到
    COMPLETE_PROFILE = 'COMPLETE_PROFILE'  # 完善个人资料
    BIND_PHONE = 'BIND_PHONE'  # 绑定手机
    BIND_EMAIL = 'BIND_EMAIL'  # 绑定邮箱
    FIRST_POST = 'FIRST_POST'  # 首次发帖
    REPLY_POST = 'REPLY_POST'  # 回复帖子
    POST_LIKED = 'POST_LIKED'  # 帖子被点赞
    POST_FAVORITED = 'POST_FAVORITED'  # 帖子被收藏
    BEST_REPLY = 'BEST_REPLY'  # 被设为最佳回复
    REPORT_VIOLATION = 'REPORT_VIOLATION'  # 举报违规核实
    
    # 内容质量
    NORMAL_POST = 'NORMAL_POST'  # 普通帖
    ELITE_POST = 'ELITE_POST'  # 精华帖
    STICKY_POST = 'STICKY_POST'  # 置顶帖
    ORIGINAL_TUTORIAL = 'ORIGINAL_TUTORIAL'  # 原创教程
    RESOURCE_SHARE = 'RESOURCE_SHARE'  # 资源分享
    
    # 特殊贡献
    MODERATOR_BONUS = 'MODERATOR_BONUS'  # 版主津贴
    EVENT_ORGANIZER = 'EVENT_ORGANIZER'  # 活动组织
    BUG_FEEDBACK = 'BUG_FEEDBACK'  # Bug反馈
    INVITE_FRIEND = 'INVITE_FRIEND'  # 邀请好友
    
    # 消耗
    ANONYMOUS_POST = 'ANONYMOUS_POST'  # 匿名发帖
    URGENT_POST = 'URGENT_POST'  # 帖子加急
    CHANGE_USERNAME = 'CHANGE_USERNAME'  # 修改用户名
    CUSTOM_TITLE = 'CUSTOM_TITLE'  # 自定义头衔
    CREATE_SECTION = 'CREATE_SECTION'  # 创建版块
    BUY_ITEM = 'BUY_ITEM'  # 购买商品
    PAY_POST_READ = 'PAY_POST_READ'  # 付费帖阅读
    BOUNTY_REWARD = 'BOUNTY_REWARD'  # 悬赏奖励
    TIP_AUTHOR = 'TIP_AUTHOR'  # 打赏作者
    
    # 系统
    SYSTEM_ADJUST = 'SYSTEM_ADJUST'  # 系统调整
    POINTS_EXPIRED = 'POINTS_EXPIRED'  # 积分过期

class PointRecord(Treet_IP_Conn.Model):
    """积分记录表"""
    __tablename__ = 'point_records'
    
    RecordID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, primary_key=True, autoincrement=True)
    UserID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('users.UserID'), nullable=False, index=True)
    ActionType = Treet_IP_Conn.Column(Treet_IP_Conn.Enum(PointActionType), nullable=False, index=True)
    Points = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, nullable=False, default=0)  # 正数为获得，负数为消耗
    Balance = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, nullable=False)  # 操作后的余额
    Description = Treet_IP_Conn.Column(Treet_IP_Conn.String(255), nullable=True)  # 操作描述
    RelatedID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, nullable=True)  # 关联ID（如帖子ID、商品ID）
    CreationTime = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    user = Treet_IP_Conn.relationship('User', backref='point_records', foreign_keys=[UserID])
    
    def __repr__(self):
        return f'<PointRecord {self.RecordID}: {self.ActionType} {self.Points}>'

class DailyCheckIn(Treet_IP_Conn.Model):
    """每日签到记录表"""
    __tablename__ = 'daily_check_ins'
    
    CheckInID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, primary_key=True, autoincrement=True)
    UserID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('users.UserID'), nullable=False, index=True)
    CheckInDate = Treet_IP_Conn.Column(Treet_IP_Conn.Date, nullable=False, index=True)  # 签到日期
    CheckInTime = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, default=datetime.utcnow)
    ConsecutiveDays = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, default=1)  # 连续签到天数
    PointsEarned = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, default=0)  # 本次获得的积分
    
    # 关系
    user = Treet_IP_Conn.relationship('User', backref='check_ins', foreign_keys=[UserID])
    
    # 唯一约束：每个用户每天只能签到一次
    __table_args__ = (
        Treet_IP_Conn.UniqueConstraint('UserID', 'CheckInDate', name='uq_user_checkin_date'),
    )
    
    def __repr__(self):
        return f'<DailyCheckIn {self.CheckInID}: User {self.UserID} on {self.CheckInDate}>'

class UserLevel(enum.Enum):
    """用户等级枚举"""
    LEVEL_1 = 1  # 萌新
    LEVEL_2 = 2  # 游民
    LEVEL_3 = 3  # 居民
    LEVEL_4 = 4  # 资深居民
    LEVEL_5 = 5  # 意见领袖
    LEVEL_6 = 6  # 社区元老
    LEVEL_7 = 7  # 传奇

class PointShopItem(Treet_IP_Conn.Model):
    """积分商城商品表"""
    __tablename__ = 'point_shop_items'
    
    ItemID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, primary_key=True, autoincrement=True)
    ItemName = Treet_IP_Conn.Column(Treet_IP_Conn.String(100), nullable=False)
    ItemType = Treet_IP_Conn.Column(Treet_IP_Conn.String(50), nullable=False, index=True)  # 商品类型：虚拟商品、实物、权益
    ItemDescription = Treet_IP_Conn.Column(Treet_IP_Conn.Text, nullable=True)
    PointsRequired = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, nullable=False)  # 所需积分
    Stock = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, default=-1)  # 库存，-1表示无限
    ImageURL = Treet_IP_Conn.Column(Treet_IP_Conn.String(255), nullable=True)  # 商品图片
    ValidityDays = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, default=0)  # 有效期（天），0表示永久
    IsActive = Treet_IP_Conn.Column(Treet_IP_Conn.Boolean, default=True, index=True)  # 是否上架
    CreationTime = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PointShopItem {self.ItemID}: {self.ItemName}>'

class PointRedemption(Treet_IP_Conn.Model):
    """积分兑换记录表"""
    __tablename__ = 'point_redemptions'
    
    RedemptionID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, primary_key=True, autoincrement=True)
    UserID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('users.UserID'), nullable=False, index=True)
    ItemID = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, Treet_IP_Conn.ForeignKey('point_shop_items.ItemID'), nullable=False)
    PointsSpent = Treet_IP_Conn.Column(Treet_IP_Conn.Integer, nullable=False)  # 消耗的积分
    RedemptionTime = Treet_IP_Conn.Column(Treet_IP_Conn.DateTime, default=datetime.utcnow, index=True)
    Status = Treet_IP_Conn.Column(Treet_IP_Conn.String(20), default='completed', nullable=False)  # completed, cancelled, refunded
    Notes = Treet_IP_Conn.Column(Treet_IP_Conn.Text, nullable=True)  # 备注
    
    # 关系
    user = Treet_IP_Conn.relationship('User', backref='point_redemptions', foreign_keys=[UserID])
    item = Treet_IP_Conn.relationship('PointShopItem', backref='redemptions', foreign_keys=[ItemID])
    
    def __repr__(self):
        return f'<PointRedemption {self.RedemptionID}: User {self.UserID} bought Item {self.ItemID}>'
