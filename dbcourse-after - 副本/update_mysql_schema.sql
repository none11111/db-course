-- MySQL数据库结构更新脚本
-- 用于将数据库表结构更新为与Flask模型一致

-- 确保使用正确的数据库
USE forum_system;

-- 更新Categories表
ALTER TABLE Categories 
ADD COLUMN "Display Order" INT NULL AFTER DescriptionCat,
ADD COLUMN "Is Active" TINYINT NOT NULL DEFAULT 1 AFTER "Display Order";

-- 更新Comments表
ALTER TABLE Comments 
ADD COLUMN LikeCount INT NULL DEFAULT 0 AFTER CommentContent,
ADD COLUMN ParentCommentID INT NULL AFTER LikeCount,
ADD COLUMN Status VARCHAR(10) NULL DEFAULT 'approved' AFTER ParentCommentID,
ADD COLUMN AIAuditResult BOOLEAN NULL AFTER Status,
ADD COLUMN AIAuditTime DATETIME NULL AFTER AIAuditResult,
ADD COLUMN IsAIAudit BOOLEAN NOT NULL DEFAULT FALSE AFTER AIAuditTime,
ADD COLUMN AuditUserID INT NULL AFTER IsAIAudit,
ADD COLUMN AuditTime DATETIME NULL AFTER AuditUserID,
ADD COLUMN ReviewComment TEXT NULL AFTER AuditTime;

-- 更新Posts表
ALTER TABLE Posts 
ADD COLUMN IsSticky BOOLEAN NOT NULL DEFAULT FALSE AFTER ViewCount,
ADD COLUMN AIAuditResult BOOLEAN NULL AFTER IsSticky,
ADD COLUMN AIAuditTime DATETIME NULL AFTER AIAuditResult,
ADD COLUMN IsAIAudit BOOLEAN NOT NULL DEFAULT FALSE AFTER AIAuditTime,
ADD COLUMN ReviewerID INT NULL AFTER IsAIAudit,
ADD COLUMN ReviewTime DATETIME NULL AFTER ReviewerID,
ADD COLUMN ReviewComment TEXT NULL AFTER ReviewTime;

-- 更新Users表
ALTER TABLE Users 
ADD COLUMN UserEmail VARCHAR(100) NULL AFTER UserName,
ADD COLUMN UserBio TEXT NULL AFTER LastLoginTime,
ADD COLUMN AvatarURL VARCHAR(255) NULL AFTER UserBio,
ADD COLUMN Reputation INT NOT NULL DEFAULT 0 AFTER AvatarURL,
ADD COLUMN Role ENUM('ADMIN', 'USER') NOT NULL DEFAULT 'USER' AFTER Reputation,
ADD COLUMN Status ENUM('active', 'inactive', 'banned') NOT NULL DEFAULT 'active' AFTER Role;

-- 创建必要的索引
CREATE INDEX idx_comments_user_id ON Comments(UserID);
CREATE INDEX idx_comments_post_id ON Comments(PostID);
CREATE INDEX idx_comments_status ON Comments(Status);
CREATE INDEX idx_comments_is_ai_audit ON Comments(IsAIAudit);
CREATE INDEX idx_posts_status ON Posts(Status);
CREATE INDEX idx_posts_is_ai_audit ON Posts(IsAIAudit);
CREATE INDEX idx_users_role ON Users(Role);
CREATE INDEX idx_users_status ON Users(Status);

-- 插入示例数据（如果需要）
INSERT IGNORE INTO Categories (CategoryID, CategoryName, DescriptionCat, "Display Order", "Is Active") 
VALUES (1, '未分类', '默认分类', 1, 1);

-- 创建示例管理员用户
INSERT IGNORE INTO Users (UserID, UserName, PasswordHash, Role, Status, RegistrationDate) 
VALUES (1, 'admin', '$pbkdf2-sha256$260000$zH6P47aW9g6pG4F0nL8fD2hE4jF0mK2jI9gO0lU8iK3bE7cA0dF2gH4jI6kL8mN0oP2qR4sT6uV8wX0yZ2', 'ADMIN', 'active', NOW());

-- 更新现有数据的状态（如果需要）
UPDATE Posts SET Status = 'approved' WHERE Status IS NULL;
UPDATE Comments SET Status = 'approved' WHERE Status IS NULL;