---
title: 更新日志
icon: fa-solid fa-clipboard-list
---

# 更新日志

<!-- 只写改动内容，新增或删减功能之类的，不需要写增强了。。。改善了这种信息，时间越往前，越靠前 -->

## 2025-06-12

- **GroupHumanVerification**：增加了扫描提示消息与 0.5 秒异步延时，优化用户在群内人机验证时的交互体验。新增逻辑包括：在扫描未验证用户前发送提示消息、在扫描操作前后插入异步延时，并同步优化了按需扫描功能的提示及延时处理。（[92341b4](https://github.com/W1ndys/W1ndysBot-dev/commit/92341b4ce95aec1865f666ec58e7fec4aaaf6dc6)）
- **文档**：更新了配置说明文档，将配置文件路径修改为 `app/.env`。（[3cc93f1](https://github.com/W1ndys/W1ndysBot-dev/commit/3cc93f1684d2b4418f24ab697fcd2a232e27eb7b)）

## 2025-06-11

- **GroupManager**：新增禁言排行榜功能，支持查询群内今日禁言之王、个人禁言时长和全服务器禁言记录，新增自我封禁功能，随机禁言 1-10 分钟，禁言时长单位由分钟调整为秒，调整禁言通知中的删除消息时长 ([c99565a](https://github.com/W1ndys/W1ndysBot-dev/commit/c99565a) [f2d5714](https://github.com/W1ndys/W1ndysBot-dev/commit/f2d5714) [8b9b3ad](https://github.com/W1ndys/W1ndysBot-dev/commit/8b9b3ad))
- **GroupBanWords**：新增忽略群管理的消息，避免群管理被误封禁 ([e79588b](https://github.com/W1ndys/W1ndysBot-dev/commit/e79588badc4cebafb71df7ae2f42af54f4687454))
- **GroupBanWords**：优化了"复制群违禁词"命令的参数校验与用户反馈，包括增加参数完整性检查、优化错误提示、复制操作前显示进度、复制成功后通知数量，提升了命令健壮性与用户交互体验 ([e81f4b0](https://github.com/W1ndys/W1ndysBot-dev/commit/e81f4b00266dcf243da302c8755806612f8605d0))
- **GroupBanWords**：新增"复制群内违禁词"功能，包括复制命令实现，命令描述 f-string 格式统一，DataManager 方法补全详细注释，实现违禁词复制及反馈，并限制仅系统管理员可用，详见命令文本注释 ([33e95eb](https://github.com/W1ndys/W1ndysBot-dev/commit/33e95eb829ea70076573f67a06d1220c54ee5f00))
- **GroupHumanVerification**：优化踢人操作与状态更新顺序，先更新成员状态为"已踢出"再执行踢人操作，避免状态与实际操作不同步，修正通知中非待验证成员的描述 ([42a337a](https://github.com/W1ndys/W1ndysBot-dev/commit/42a337a))
- **Reporter**：修改私聊消息处理逻辑，新增格式化文本通知和 CQ 码消息发送，分离原始消息和信息，优化消息忽略匹配，增加群号信息显示 ([c919f86](https://github.com/W1ndys/W1ndysBot-dev/commit/c919f86) [f2b29e1](https://github.com/W1ndys/W1ndysBot-dev/commit/f2b29e1))
- **AutoRepeat**：调整随机概率，戳一戳概率 10% ([eed78f5](https://github.com/W1ndys/W1ndysBot-dev/commit/eed78f5a3d55b200d0eb23b4a5c0ecddac65eae9))
- **EventHandler**：修改 EventHandler 类以支持 WebSocket 连接，增加模块加载状态上报功能，并记录加载成功和失败的模块信息 ([24271f8](https://github.com/W1ndys/W1ndysBot-dev/commit/24271f8fd36f69cb13c4901b03a2187497d5737c))
- **Core**：修改了群开关，相关功能全部更为群主管理可以自助开关，菜单命令拼接改成 f-string 拼接 ([f23d4dc](https://github.com/W1ndys/W1ndysBot-dev/commit/f23d4dcc867aee03ab391e6e38aa7dbe6bb25ccb))
- **Reporter**：新增消息忽略功能，忽略 UUID 格式消息，避免重复上报 ([0a0dc8d](https://github.com/W1ndys/W1ndysBot-dev/commit/9157ee86615279feb478c1d4467794f11920c6b8))

## 2025-06-10

- **GroupNickNameLock**：移除入群修改默认名的设定 ([0a0dc8d](https://github.com/W1ndys/W1ndysBot-dev/commit/0a0dc8d9832d0c9ba060c97ce421a412679d6cc4))
- **GroupBanWords**：新增敏感词管理功能，在 DataManager 类中添加更新时间字段，优化敏感词添加和更新逻辑，支持记录敏感词更新时间 ([3e56c36](https://github.com/W1ndys/W1ndysBot-dev/commit/3e56c362b5d3ec1a09e0354f2163aaccaf73ce0b))
- **GroupBanWords**：新增管理员解封和踢出用户命令处理功能，支持管理员通过私聊命令解除被封禁用户状态或将违规用户踢出群聊，优化违禁词检测与用户状态管理 ([6f93fa1](https://github.com/W1ndys/W1ndysBot-dev/commit/6f93fa10933c959ac44ebbbc037e00020019bae9))
- **GroupBanWords**：新增添加和删除违禁词命令处理，更新数据管理类支持用户状态管理，实现消息权重计算和自动封禁违规用户 ([62672a6](https://github.com/W1ndys/W1ndysBot-dev/commit/62672a67d444b0b004ba36c2461fd7b034de7dda))
- **InviteTreeRecord**：新增邀请次数统计功能，在 InviteLinkRecordDataManager 中添加 get_invite_count 方法，用于统计邀请者在群中的邀请人数，在 GroupNoticeHandler 中通知管理员被邀请者的邀请次数 ([b304dcf](https://github.com/W1ndys/W1ndysBot-dev/commit/b304dcf5d31e2944e67ca29f8c8d1c4e7522a5c3))

## 2025-06-09

- **Logger**：修改日志文件命名方式，去掉前缀"app\_"，仅保留时间戳，修改 namer 函数，轮转时以当前时间命名新日志文件，格式为 YYYY-MM-DD_HH-MM-SS.log ([6bf19ce](https://github.com/W1ndys/W1ndysBot-dev/commit/6bf19ce961b09a138e10b173024c3d29818ac061))
- **GroupSpamDetection**：修改重复消息检测逻辑，仅检查最近一分钟内的消息，更新日志信息 ([da74eac](https://github.com/W1ndys/W1ndysBot-dev/commit/da74eac964ff07780c8cac82b93d221e24254105))
- **EventHandler**：在事件处理程序中添加群 ID 信息到消息格式化 ([92673f9](https://github.com/W1ndys/W1ndysBot-dev/commit/92673f9cb5fc96e75115ce7ff5d569afab72920c))
- **MenuManager**：将菜单命令定义移至`menu_manager.py`，更新多个模块以引用新的`MENU_COMMAND` ([adfcbd2](https://github.com/W1ndys/W1ndysBot-dev/commit/adfcbd2))
- **AutoRepeat**：新增随机戳一戳功能，概率 30% ([aaa6f44](https://github.com/W1ndys/W1ndysBot-dev/commit/aaa6f44))
- **GroupMessageHandler**：修改群聊复读消息发送逻辑 ([e551fb2](https://github.com/W1ndys/W1ndysBot-dev/commit/e551fb2))

## 2025-06-08

- **GroupSpamDetection**：禁言时间改为 3 分钟，优化图片处理，所有图片视为相同消息 ([f9f2da7](https://github.com/W1ndys/W1ndysBot-dev/commit/f9f2da7))
- **GroupNickNameLock**：修复个人群昵称锁与数据库一致时，会来回修改群昵称的问题 ([d80ea77](https://github.com/W1ndys/W1ndysBot-dev/commit/d80ea77))
- **KeywordsReply**：完成关键词回复模块的开发，新增菜单命令处理功能，优化关键词回复逻辑，支持完全匹配，只回复内容，不会回复其他多余文字，是 FAQ 系统的补充，不设置权限，任何人都可以添加关键词回复，但只有管理员可以删除关键词回复 ([b4acfea](https://github.com/W1ndys/W1ndysBot-dev/commit/b4acfea) [d19f357](https://github.com/W1ndys/W1ndysBot-dev/commit/d19f357))

## 2025-06-07

- **GroupNickNameLock**：优化群昵称锁定命令的处理逻辑，更新命令描述以提升可读性和用户体验 ([dcdce17](https://github.com/W1ndys/W1ndysBot-dev/commit/dcdce17))
- **KeywordsReply**：新增关键词回复模块，完全匹配，只回复内容，不会回复其他多余文字，是 FAQ 系统的补充，不设置权限，任何人都可以添加关键词回复，但只有管理员可以删除关键词回复 ([e31fee1](https://github.com/W1ndys/W1ndysBot-dev/commit/e31fee1) [d8d32ca](https://github.com/W1ndys/W1ndysBot-dev/commit/d8d32ca))
- **GroupNickNameLock**：优化群消息处理逻辑，仅处理英文中括号的 Unicode，提升消息解析准确性 ([c7ff845](https://github.com/W1ndys/W1ndysBot-dev/commit/c7ff845))
- **Reporter**：优化私聊消息格式，增强用户信息展示，提升用户体验 ([055ef03](https://github.com/W1ndys/W1ndysBot-dev/commit/055ef03))

## 2025-06-06

- **GroupNickNameLock**：在群昵称锁定模块中新增昵称提醒时间间隔功能，优化数据库表结构以支持提醒时间记录，新增群昵称提醒功能，当群昵称不符合正则时，会提醒用户修改，并且当群设置了默认名时，用户群名片不符正则时，才自动设置默认名 ([7dbee83](https://github.com/W1ndys/W1ndysBot-dev/commit/7dbee83))
- **Core**：**核心模块新增动态加载菜单，模块功能、描述等信息，实现模块的动态加载** ([2eb8d74](https://github.com/W1ndys/W1ndysBot-dev/commit/2eb8d74))
- **Switch/Command**：重构开关功能和命令输出功能，全部整合到 Core 核心模块内，并且修复开关命令的权限控制未鉴权的问题 ([c32b4a6](https://github.com/W1ndys/W1ndysBot-dev/commit/c32b4a6))
- **GroupHumanVerification**：在群人机验证模块中新增仅扫描当前群聊未验证成员的功能，优化警告和踢出逻辑，提升群管理体验。([4fae9dc](https://github.com/W1ndys/W1ndysBot-dev/commit/4fae9dc))

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
