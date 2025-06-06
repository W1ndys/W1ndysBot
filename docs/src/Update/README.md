---
title: 更新日志
icon: fa-solid fa-clipboard-list
---

# 更新日志

## 2025-06-06

- **GroupNickNameLock**：在群昵称锁定模块中新增昵称提醒时间间隔功能，优化数据库表结构以支持提醒时间记录，新增群昵称提醒功能，当群昵称不符合正则时，会提醒用户修改，并且当群设置了默认名时，用户群名片不符正则时，才自动设置默认名
- **Core**：**核心模块新增动态加载菜单，模块功能、描述等信息，实现模块的动态加载**
- **Switch/Command**：重构开关功能和命令输出功能，全部整合到 Core 核心模块内，并且修复开关命令的权限控制未鉴权的问题
- **GroupHumanVerification**：在群人机验证模块中新增仅扫描当前群聊未验证成员的功能，优化警告和踢出逻辑，提升群管理体验。

## 2025-06-05

- **GroupHumanVerification**：被踢逻辑优化，仅处理非机器人号踢人事件，减少多次通知
- **GroupHumanVerification**： 优化退群和踢人通知逻辑，新增消息 ID 字段，优化撤回消息功能
- **GroupHumanVerification**：优化用户警告消息格式，增加一次换行，调整验证码提示为更易读的格式
- **GroupHumanVerification**：在群人机验证模块中增加消息删除逻辑，优化解除禁言后的消息处理
- **GroupNickNameLock**：优化群名片设置逻辑，新增群成员通知时自动设置默认名功能，并且当群设置了默认名时，用户群名片不符正则时，才自动设置默认名

## 2025-06-04

- **系统**：在 BlackList、Doro、FAQSystem、Reporter、InviteTreeRecord、Template、WordCloud 和 GroupHumanVerification 模块中实现通用的菜单命令接口
- **GroupHumanVerification**：优化验证码匹配逻辑，支持根据用户复制消息全部内容进行验证
- **GroupHumanVerification**：新增 UUID 提取功能，优化用户命令处理逻辑
- **GroupHumanVerification**：优化被踢通知和逻辑，增加拒绝状态的提示信息
- **Menu**：多个模块新增菜单命令处理功能
- **Script**：新增多个脚本，支持 Linux 和 Windows 环境下的 Python 虚拟环境创建、应用启动、停止和重启功能
- **Template**：修改模板模块的开关名称为 "tp"，新增菜单命令处理功能
- **Reporter**：修改 Reporter 模块的开关名称，将其从 "reporter" 简化为 "rp"
- **Permission**：精简群管理模块中的错误处理逻辑，移除冗余的用户 ID 验证和错误消息发送
- **GroupHumanVerification**：优化消息格式，调整禁言解除通知的文本内容，同时修改验证码提示的格式
- **GroupHumanVerification**：优化用户警告消息格式，调整验证码提示为更易读的格式
- **GroupHumanVerification**：优化群聊成员减少通知逻辑，增加对退群成员的标记，非未验证状态也会通知
- **GroupHumanVerification**：新增验证成功后，撤回验证码那条消息的功能

## 2025-06-03

- **GroupHumanVerification**：优化用户警告消息的生成逻辑，新增用户超出警告次数的统一通知
- **GroupHumanVerification**：优化验证码中用户提醒消息生成逻辑，区分@和文本消息
- **GroupMuteUnlock**：新增解码 unicode 字符串的功能，优化群消息处理逻辑
- **OnlineTest**：增强管理员 ID 的显示
- **Log**：修改日志文件命名规则，新增自定义 Xnamer 函数以支持轮转序号

## 2025-06-02

- **GroupHumanVerification**：重构数据管理逻辑，优化数据库表结构，支持警告次数和状态管理，新增群组 ID 处理逻辑，优化群成员被踢/退群/解禁等通知，移除冗余代码，增强模块可维护性

## 2025-06-01

- **API**：新增合并转发消息功能
- **GroupHumanVerification**：新增被解禁自动通过验证

## 2025-05-31

- 从现在开始，更新日志将记录在这里，此前已完成的功能将不再记录
