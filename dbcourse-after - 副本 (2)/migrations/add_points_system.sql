-- 为用户表添加积分相关字段
ALTER TABLE users ADD COLUMN Points INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN Level INTEGER DEFAULT 1;
ALTER TABLE users ADD COLUMN TotalPointsEarned INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN ConsecutiveCheckInDays INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN LastCheckInDate DATE;
ALTER TABLE users ADD COLUMN IsPhoneBound BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN IsEmailBound BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN IsProfileCompleted BOOLEAN DEFAULT 0;

-- 创建积分记录表
CREATE TABLE IF NOT EXISTS point_records (
    RecordID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER NOT NULL,
    ActionType TEXT NOT NULL,
    Points INTEGER NOT NULL DEFAULT 0,
    Balance INTEGER NOT NULL,
    Description TEXT,
    RelatedID INTEGER,
    CreationTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES users(UserID)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_point_records_user ON point_records(UserID);
CREATE INDEX IF NOT EXISTS idx_point_records_action ON point_records(ActionType);
CREATE INDEX IF NOT EXISTS idx_point_records_time ON point_records(CreationTime);

-- 创建每日签到记录表
CREATE TABLE IF NOT EXISTS daily_check_ins (
    CheckInID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER NOT NULL,
    CheckInDate DATE NOT NULL,
    CheckInTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    ConsecutiveDays INTEGER DEFAULT 1,
    PointsEarned INTEGER DEFAULT 0,
    FOREIGN KEY (UserID) REFERENCES users(UserID),
    UNIQUE(UserID, CheckInDate)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_daily_check_ins_user ON daily_check_ins(UserID);
CREATE INDEX IF NOT EXISTS idx_daily_check_ins_date ON daily_check_ins(CheckInDate);

-- 创建积分商城商品表
CREATE TABLE IF NOT EXISTS point_shop_items (
    ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemName TEXT NOT NULL,
    ItemType TEXT NOT NULL,
    ItemDescription TEXT,
    PointsRequired INTEGER NOT NULL,
    Stock INTEGER DEFAULT -1,
    ImageURL TEXT,
    ValidityDays INTEGER DEFAULT 0,
    IsActive BOOLEAN DEFAULT 1,
    CreationTime DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_point_shop_items_type ON point_shop_items(ItemType);
CREATE INDEX IF NOT EXISTS idx_point_shop_items_active ON point_shop_items(IsActive);

-- 创建积分兑换记录表
CREATE TABLE IF NOT EXISTS point_redemptions (
    RedemptionID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER NOT NULL,
    ItemID INTEGER NOT NULL,
    PointsSpent INTEGER NOT NULL,
    RedemptionTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    Status TEXT DEFAULT 'completed',
    Notes TEXT,
    FOREIGN KEY (UserID) REFERENCES users(UserID),
    FOREIGN KEY (ItemID) REFERENCES point_shop_items(ItemID)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_point_redemptions_user ON point_redemptions(UserID);
CREATE INDEX IF NOT EXISTS idx_point_redemptions_item ON point_redemptions(ItemID);
CREATE INDEX IF NOT EXISTS idx_point_redemptions_time ON point_redemptions(RedemptionTime);
