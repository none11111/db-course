from app.models.points import PointRecord, PointActionType, DailyCheckIn, PointShopItem, PointRedemption
from app.models.user import User
from app import Treet_IP_Conn
from datetime import datetime, date
from flask import flash

class PointService:
    """积分服务类"""
    
    @staticmethod
    def add_points(user_id, points, action_type, description=None, related_id=None):
        """
        添加积分
        
        Args:
            user_id: 用户ID
            points: 积分数量（正数为获得，负数为消耗）
            action_type: 积分操作类型
            description: 操作描述
            related_id: 关联ID
        """
        user = User.query.get(user_id)
        if not user:
            return False
        
        old_balance = user.Points or 0
        new_balance = old_balance + points
        
        # 检查积分是否足够（消耗时）
        if points < 0 and new_balance < 0:
            flash('积分不足', 'danger')
            return False
        
        # 更新用户积分
        user.Points = new_balance
        user.TotalPointsEarned = max(user.TotalPointsEarned or 0, user.TotalPointsEarned + max(0, points))
        
        # 更新用户等级
        PointService.update_user_level(user)
        
        # 创建积分记录
        record = PointRecord(
            UserID=user_id,
            ActionType=action_type,
            Points=points,
            Balance=new_balance,
            Description=description or PointService.get_action_description(action_type),
            RelatedID=related_id
        )
        
        Treet_IP_Conn.session.add(record)
        Treet_IP_Conn.session.commit()
        
        return True
    
    @staticmethod
    def get_action_description(action_type):
        """获取积分操作类型的描述"""
        descriptions = {
            PointActionType.DAILY_CHECK_IN: '每日签到',
            PointActionType.COMPLETE_PROFILE: '完善个人资料',
            PointActionType.BIND_PHONE: '绑定手机',
            PointActionType.BIND_EMAIL: '绑定邮箱',
            PointActionType.FIRST_POST: '首日发帖',
            PointActionType.REPLY_POST: '回复帖子',
            PointActionType.POST_LIKED: '帖子被点赞',
            PointActionType.POST_FAVORITED: '帖子被收藏',
            PointActionType.BEST_REPLY: '被设为最佳回复',
            PointActionType.REPORT_VIOLATION: '举报违规核实',
            PointActionType.NORMAL_POST: '发布帖子',
            PointActionType.ELITE_POST: '精华帖',
            PointActionType.STICKY_POST: '置顶帖',
            PointActionType.ORIGINAL_TUTORIAL: '原创教程',
            PointActionType.RESOURCE_SHARE: '资源分享',
            PointActionType.MODERATOR_BONUS: '版主津贴',
            PointActionType.EVENT_ORGANIZER: '活动组织',
            PointActionType.BUG_FEEDBACK: 'Bug反馈',
            PointActionType.INVITE_FRIEND: '邀请好友',
            PointActionType.ANONYMOUS_POST: '匿名发帖',
            PointActionType.URGENT_POST: '帖子加急',
            PointActionType.CHANGE_USERNAME: '修改用户名',
            PointActionType.CUSTOM_TITLE: '自定义头衔',
            PointActionType.CREATE_SECTION: '创建版块',
            PointActionType.BUY_ITEM: '购买商品',
            PointActionType.PAY_POST_READ: '付费帖阅读',
            PointActionType.BOUNTY_REWARD: '悬赏奖励',
            PointActionType.TIP_AUTHOR: '打赏作者',
            PointActionType.SYSTEM_ADJUST: '系统调整',
            PointActionType.POINTS_EXPIRED: '积分过期',
        }
        return descriptions.get(action_type, '未知操作')
    
    @staticmethod
    def update_user_level(user):
        """根据积分更新用户等级"""
        level = PointService.calculate_level(user.Points)
        if user.Level != level:
            user.Level = level
    
    @staticmethod
    def calculate_level(points):
        """根据积分计算用户等级"""
        if points >= 30000:
            return 7
        elif points >= 10000:
            return 6
        elif points >= 5000:
            return 5
        elif points >= 2000:
            return 4
        elif points >= 500:
            return 3
        elif points >= 100:
            return 2
        else:
            return 1
    
    @staticmethod
    def get_level_name(level):
        """获取等级名称"""
        level_names = {
            1: '萌新',
            2: '游民',
            3: '居民',
            4: '资深居民',
            5: '意见领袖',
            6: '社区元老',
            7: '传奇',
        }
        return level_names.get(level, '未知')
    
    @staticmethod
    def check_daily_limit(user_id, action_type, limit):
        """检查每日限制"""
        today = date.today()
        count = PointRecord.query.filter(
            PointRecord.UserID == user_id,
            PointRecord.ActionType == action_type,
            PointRecord.CreationTime >= datetime.combine(today, datetime.min.time())
        ).count()
        return count < limit
    
    @staticmethod
    def check_in(user_id):
        """每日签到"""
        user = User.query.get(user_id)
        if not user:
            return False, '用户不存在'
        
        today = date.today()
        
        # 检查今天是否已经签到
        existing = DailyCheckIn.query.filter_by(UserID=user_id, CheckInDate=today).first()
        if existing:
            return False, '今天已经签到过了'
        
        # 计算连续签到天数
        yesterday = date.fromordinal(today.toordinal() - 1)
        yesterday_checkin = DailyCheckIn.query.filter_by(UserID=user_id, CheckInDate=yesterday).first()
        
        consecutive_days = 1
        if yesterday_checkin:
            consecutive_days = yesterday_checkin.ConsecutiveDays + 1
        
        # 计算积分
        points = 2  # 基础积分
        if consecutive_days >= 30:
            points += 20  # 连续30天额外+20
        elif consecutive_days >= 7:
            points += 5  # 连续7天额外+5
        
        # 创建签到记录
        checkin = DailyCheckIn(
            UserID=user_id,
            CheckInDate=today,
            CheckInTime=datetime.utcnow(),
            ConsecutiveDays=consecutive_days,
            PointsEarned=points
        )
        
        # 更新用户信息
        user.ConsecutiveCheckInDays = consecutive_days
        user.LastCheckInDate = today
        
        # 添加积分
        PointService.add_points(
            user_id=user_id,
            points=points,
            action_type=PointActionType.DAILY_CHECK_IN,
            description=f'每日签到（连续{consecutive_days}天）',
            related_id=checkin.CheckInID
        )
        
        Treet_IP_Conn.session.add(checkin)
        Treet_IP_Conn.session.commit()
        
        return True, f'签到成功！获得{points}积分'
    
    @staticmethod
    def complete_profile(user_id):
        """完善个人资料"""
        user = User.query.get(user_id)
        if not user:
            return False
        
        if user.IsProfileCompleted:
            return False, '已经完善过个人资料'
        
        # 检查是否完善了所有信息
        if not user.UserBio or not user.AvatarURL:
            return False, '请完善头像和个人简介'
        
        user.IsProfileCompleted = True
        Treet_IP_Conn.session.commit()
        
        PointService.add_points(
            user_id=user_id,
            points=10,
            action_type=PointActionType.COMPLETE_PROFILE
        )
        
        return True, '完善个人资料成功！获得10积分'
    
    @staticmethod
    def bind_phone(user_id):
        """绑定手机"""
        user = User.query.get(user_id)
        if not user:
            return False
        
        if user.IsPhoneBound:
            return False, '已经绑定过手机'
        
        user.IsPhoneBound = True
        Treet_IP_Conn.session.commit()
        
        PointService.add_points(
            user_id=user_id,
            points=5,
            action_type=PointActionType.BIND_PHONE
        )
        
        return True, '绑定手机成功！获得5积分'
    
    @staticmethod
    def bind_email(user_id):
        """绑定邮箱"""
        user = User.query.get(user_id)
        if not user:
            return False
        
        if user.IsEmailBound:
            return False, '已经绑定过邮箱'
        
        user.IsEmailBound = True
        Treet_IP_Conn.session.commit()
        
        PointService.add_points(
            user_id=user_id,
            points=5,
            action_type=PointActionType.BIND_EMAIL
        )
        
        return True, '绑定邮箱成功！获得5积分'
    
    @staticmethod
    def first_post(user_id, post_id):
        """首日发帖"""
        if not PointService.check_daily_limit(user_id, PointActionType.FIRST_POST, 1):
            return False, '今天已经发过首帖了'
        
        PointService.add_points(
            user_id=user_id,
            points=3,
            action_type=PointActionType.FIRST_POST,
            related_id=post_id
        )
        
        return True, '首日发帖成功！获得3积分'
    
    @staticmethod
    def reply_post(user_id, comment_id):
        """回复帖子"""
        if not PointService.check_daily_limit(user_id, PointActionType.REPLY_POST, 5):
            return False, '今天回复次数已达上限'
        
        PointService.add_points(
            user_id=user_id,
            points=1,
            action_type=PointActionType.REPLY_POST,
            related_id=comment_id
        )
        
        return True, '回复成功！获得1积分'
    
    @staticmethod
    def post_liked(user_id, post_id):
        """帖子被点赞"""
        if not PointService.check_daily_limit(user_id, PointActionType.POST_LIKED, 10):
            return False, '今日点赞奖励已达上限'
        
        PointService.add_points(
            user_id=user_id,
            points=1,
            action_type=PointActionType.POST_LIKED,
            related_id=post_id
        )
        
        return True, '帖子被点赞！获得1积分'
    
    @staticmethod
    def post_favorited(user_id, post_id):
        """帖子被收藏"""
        if not PointService.check_daily_limit(user_id, PointActionType.POST_FAVORITED, 10):
            return False, '今日收藏奖励已达上限'
        
        PointService.add_points(
            user_id=user_id,
            points=2,
            action_type=PointActionType.POST_FAVORITED,
            related_id=post_id
        )
        
        return True, '帖子被收藏！获得2积分'
    
    @staticmethod
    def best_reply(user_id, comment_id):
        """被设为最佳回复"""
        PointService.add_points(
            user_id=user_id,
            points=10,
            action_type=PointActionType.BEST_REPLY,
            related_id=comment_id
        )
        
        return True, '被设为最佳回复！获得10积分'
    
    @staticmethod
    def report_violation(user_id):
        """举报违规核实"""
        if not PointService.check_daily_limit(user_id, PointActionType.REPORT_VIOLATION, 5):
            return False, '今日举报奖励已达上限'
        
        PointService.add_points(
            user_id=user_id,
            points=2,
            action_type=PointActionType.REPORT_VIOLATION
        )
        
        return True, '举报违规核实！获得2积分'
    
    @staticmethod
    def elite_post(user_id, post_id):
        """精华帖"""
        PointService.add_points(
            user_id=user_id,
            points=50,
            action_type=PointActionType.ELITE_POST,
            related_id=post_id
        )
        
        return True, '精华帖！获得50积分'
    
    @staticmethod
    def sticky_post(user_id, post_id):
        """置顶帖"""
        PointService.add_points(
            user_id=user_id,
            points=100,
            action_type=PointActionType.STICKY_POST,
            related_id=post_id
        )
        
        return True, '置顶帖！获得100积分'
    
    @staticmethod
    def original_tutorial(user_id, post_id):
        """原创教程"""
        PointService.add_points(
            user_id=user_id,
            points=80,
            action_type=PointActionType.ORIGINAL_TUTORIAL,
            related_id=post_id
        )
        
        return True, '原创教程！获得80积分'
    
    @staticmethod
    def resource_share(user_id):
        """资源分享"""
        PointService.add_points(
            user_id=user_id,
            points=30,
            action_type=PointActionType.RESOURCE_SHARE
        )
        
        return True, '资源分享！获得30积分'
