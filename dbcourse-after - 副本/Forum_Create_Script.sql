/*==============================================================*/
/* DBMS name:      Microsoft SQL Server 2012                    */
/* Created on:     2025/11/27 10:12:24                          */
/*==============================================================*/


if exists (select 1
   from sys.sysreferences r join sys.sysobjects o on (o.id = r.constid and o.type = 'F')
   where r.fkeyid = object_id('Comments') and o.name = 'FK_COMMENTS_BELONGS_T_POSTS')
alter table Comments
   drop constraint FK_COMMENTS_BELONGS_T_POSTS
go

if exists (select 1
   from sys.sysreferences r join sys.sysobjects o on (o.id = r.constid and o.type = 'F')
   where r.fkeyid = object_id('Comments') and o.name = 'FK_COMMENTS_WRITES_USERS')
alter table Comments
   drop constraint FK_COMMENTS_WRITES_USERS
go

if exists (select 1
   from sys.sysreferences r join sys.sysobjects o on (o.id = r.constid and o.type = 'F')
   where r.fkeyid = object_id('Posts') and o.name = 'FK_POSTS_CLASSIFIE_CATEGORI')
alter table Posts
   drop constraint FK_POSTS_CLASSIFIE_CATEGORI
go

if exists (select 1
   from sys.sysreferences r join sys.sysobjects o on (o.id = r.constid and o.type = 'F')
   where r.fkeyid = object_id('Posts') and o.name = 'FK_POSTS_PUBLISHES_USERS')
alter table Posts
   drop constraint FK_POSTS_PUBLISHES_USERS
go

if exists (select 1
   from sys.sysreferences r join sys.sysobjects o on (o.id = r.constid and o.type = 'F')
   where r.fkeyid = object_id('posttags') and o.name = 'FK_POSTTAGS_POSTTAGS_POSTS')
alter table posttags
   drop constraint FK_POSTTAGS_POSTTAGS_POSTS
go

if exists (select 1
   from sys.sysreferences r join sys.sysobjects o on (o.id = r.constid and o.type = 'F')
   where r.fkeyid = object_id('posttags') and o.name = 'FK_POSTTAGS_POSTTAGS2_TAGS')
alter table posttags
   drop constraint FK_POSTTAGS_POSTTAGS2_TAGS
go

if exists (select 1
            from  sysobjects
           where  id = object_id('Categories')
            and   type = 'U')
   drop table Categories
go

if exists (select 1
            from  sysindexes
           where  id    = object_id('Comments')
            and   name  = 'Belongs_to_FK'
            and   indid > 0
            and   indid < 255)
   drop index Comments.Belongs_to_FK
go

if exists (select 1
            from  sysindexes
           where  id    = object_id('Comments')
            and   name  = 'Writes_FK'
            and   indid > 0
            and   indid < 255)
   drop index Comments.Writes_FK
go

if exists (select 1
            from  sysobjects
           where  id = object_id('Comments')
            and   type = 'U')
   drop table Comments
go

if exists (select 1
            from  sysindexes
           where  id    = object_id('Posts')
            and   name  = 'Classifies_FK'
            and   indid > 0
            and   indid < 255)
   drop index Posts.Classifies_FK
go

if exists (select 1
            from  sysindexes
           where  id    = object_id('Posts')
            and   name  = 'Publishes_FK'
            and   indid > 0
            and   indid < 255)
   drop index Posts.Publishes_FK
go

if exists (select 1
            from  sysobjects
           where  id = object_id('Posts')
            and   type = 'U')
   drop table Posts
go

if exists (select 1
            from  sysobjects
           where  id = object_id('Tags')
            and   type = 'U')
   drop table Tags
go

if exists (select 1
            from  sysobjects
           where  id = object_id('Users')
            and   type = 'U')
   drop table Users
go

if exists (select 1
            from  sysindexes
           where  id    = object_id('posttags')
            and   name  = 'posttags2_FK'
            and   indid > 0
            and   indid < 255)
   drop index posttags.posttags2_FK
go

if exists (select 1
            from  sysindexes
           where  id    = object_id('posttags')
            and   name  = 'posttags_FK'
            and   indid > 0
            and   indid < 255)
   drop index posttags.posttags_FK
go

if exists (select 1
            from  sysobjects
           where  id = object_id('posttags')
            and   type = 'U')
   drop table posttags
go

/*==============================================================*/
/* Table: Categories                                            */
/*==============================================================*/
create table Categories (
   CategoryID           int                  not null,
   CategoryName         varchar(50)          not null,
   DescriptionCat       varchar(500)         null,
   "Display Order"      int                  null,
   "Is Active"          bit                  not null default 1,
   constraint PK_CATEGORIES primary key nonclustered (CategoryID)
)
go

/*==============================================================*/
/* Table: Comments                                              */
/*==============================================================*/
create table Comments (
   CommentID            int                  not null,
   PostID               int                  not null,
   UserID               int                  not null,
   Content              text                 not null,
  "Creation Time"      datetime             not null default getdate(),  /* 这里改了：timestamp → datetime */
   "Like Count"         int                  null default 0,
   ParentCommentID      int                  null,
   Status               varchar(10)          null
      constraint CKC_STATUS_COMMENTS check (Status is null or (Status in ('published','draft','deleted'))),
   constraint PK_COMMENTS primary key nonclustered (CommentID)
)
go

/*==============================================================*/
/* Index: Writes_FK                                             */
/*==============================================================*/
create index Writes_FK on Comments (
UserID ASC
)
go

/*==============================================================*/
/* Index: Belongs_to_FK                                         */
/*==============================================================*/
create index Belongs_to_FK on Comments (
PostID ASC
)
go

/*==============================================================*/
/* Table: Posts                                                 */
/*==============================================================*/
create table Posts (
   PostID               int                  not null,
   CategoryID           int                  null,
   UserID               int                  null,
   PostTitle            varchar(200)         not null,
   PublishTime          datetime             not null default getdate(),
   PostContent          text                 not null,
   CreationTime         datetime             not null default getdate(),
   LastModified         datetime             null,
   Status               varchar(10)          not null
      constraint CKC_STATUS_POSTS check (Status in ('published','draft','deleted')),
   ViewCount            int                  not null default 0,
   constraint PK_POSTS primary key nonclustered (PostID)
)
go

/*==============================================================*/
/* Index: Publishes_FK                                          */
/*==============================================================*/
create index Publishes_FK on Posts (
UserID ASC
)
go

/*==============================================================*/
/* Index: Classifies_FK                                         */
/*==============================================================*/
create index Classifies_FK on Posts (
CategoryID ASC
)
go

/*==============================================================*/
/* Table: Tags                                                  */
/*==============================================================*/
create table Tags (
   TagID                int                  not null,
   Tagname              varchar(50)          null,
   UsageCount           int                  null default 0,
   DescriptionTag       varchar(500)         null,
   constraint PK_TAGS primary key nonclustered (TagID)
)
go

/*==============================================================*/
/* Table: Users                                                 */
/*==============================================================*/
create table Users (
   UserID               int                  not null,
   UserName             varchar(50)          null,
   RegistrationDate     datetime             null default getdate(),
   PasswordHash         varchar(225)         null,
   Avatar               varchar(225)         null,
   LastLoginTime        datetime             null,
   constraint PK_USERS primary key nonclustered (UserID)
)
go

/*==============================================================*/
/* Table: posttags                                              */
/*==============================================================*/
create table posttags (
   PostID               int                  not null,
   TagID                int                  not null,
   constraint PK_POSTTAGS primary key (PostID, TagID)
)
go

/*==============================================================*/
/* Index: posttags_FK                                           */
/*==============================================================*/
create index posttags_FK on posttags (
PostID ASC
)
go

/*==============================================================*/
/* Index: posttags2_FK                                          */
/*==============================================================*/
create index posttags2_FK on posttags (
TagID ASC
)
go

alter table Comments
   add constraint FK_COMMENTS_BELONGS_T_POSTS foreign key (PostID)
      references Posts (PostID)
go

alter table Comments
   add constraint FK_COMMENTS_WRITES_USERS foreign key (UserID)
      references Users (UserID)
go

alter table Posts
   add constraint FK_POSTS_CLASSIFIE_CATEGORI foreign key (CategoryID)
      references Categories (CategoryID)
go

alter table Posts
   add constraint FK_POSTS_PUBLISHES_USERS foreign key (UserID)
      references Users (UserID)
go

alter table posttags
   add constraint FK_POSTTAGS_POSTTAGS_POSTS foreign key (PostID)
      references Posts (PostID)
go

alter table posttags
   add constraint FK_POSTTAGS_POSTTAGS2_TAGS foreign key (TagID)
      references Tags (TagID)
go

-- 插入示例用户
INSERT INTO Users (UserID, UserName) VALUES (1, '张三'), (2, '李四');

-- 插入示例版块
INSERT INTO Categories (CategoryID, CategoryName, DescriptionCat) 
VALUES (1, '技术交流', '编程技术讨论区');

-- 插入示例帖子
INSERT INTO Posts (PostID, UserID, CategoryID, PostTitle, PostContent, Status)
VALUES (1, 1, 1, '欢迎来到论坛！', '这是第一个测试帖子', 'published');

-- 查询所有用户及其帖子数量
SELECT u.UserName, COUNT(p.PostID) as PostCount
FROM Users u 
LEFT JOIN Posts p ON u.UserID = p.UserID
GROUP BY u.UserName;

-- 查询某个版块下的所有帖子
SELECT p.PostTitle, u.UserName, p.CreationTime
FROM Posts p
JOIN Users u ON p.UserID = u.UserID
WHERE p.CategoryID = 1;
