---
title: 更新日志
icon: fa-solid fa-clipboard-list
---

# 更新日志

<!-- 只写改动内容，新增或删减功能之类的，不需要写增强了。。。改善了这种信息，时间越往前，越靠前 -->

## 2025-06-19

- **API**：增强`set_group_add_request`函数的参数和返回值文档，明确 websocket 连接、请求 id、同意标志及拒绝理由的用途，提升代码可读性和可维护性（[a5c0f4a](https://github.com/W1ndys/W1ndysBot-dev/commit/a5c0f4a3d5e99c0f5ea714b2ae3b579696f1eb86)）
- **Logger**：重构日志记录器，增强可配置性。将日志级别参数重命名为`console_level`，设置根日志为 DEBUG，调整控制台和文件处理器级别设置逻辑，新增`set_console_level`方法支持动态调整（[30d7ae6](https://github.com/W1ndys/W1ndysBot-dev/commit/30d7ae68daea037e2be09b4d49356971c512e14f)）
- **GroupHumanVerification**：增强加群请求处理逻辑。新增群 ID 属性，支持群内及私聊通知管理员，自动同意请求，记录请求时间、群 ID、用户 ID 和请求内容，提升群管理效率与体验（[74c3458](https://github.com/W1ndys/W1ndysBot-dev/commit/74c345888e5e5702ab1073d14fd77e33e10b82af)）
- **InviteTreeRecord**：重构用户邀请者查询逻辑，提取获取相关用户与根节点方法，简化`get_full_invite_chain_str`结构，保持功能不变（[b17fbba](https://github.com/W1ndys/W1ndysBot-dev/commit/b17fbba4fcc7253d75ca91733bf3853dea2d5e57)）
- **InviteTreeRecord**：增加批量删除用户相关邀请记录功能，支持管理员批量删除用户在群内的所有邀请记录，完善踢出邀请树命令的权限校验与移除逻辑（[911bcdf](https://github.com/W1ndys/W1ndysBot-dev/commit/911bcdf9effb4bb87ba8d34205e60aca5024bb0a)）

## 2025-06-18

- **FAQSystem**：优化 FAQ 数据库管理功能，支持为每个群组创建独立 FAQ 表，实现获取所有群组 ID 和删除群组数据的新方法，并更新数据库操作逻辑以适应新的结构，提升灵活性与可维护性（[54e4bca](https://github.com/W1ndys/W1ndysBot-dev/commit/54e4bca866b38448d7767eeef1d29da30f450825)）
- **README**：更新 README 文件，添加卷卷的交流小窝链接和框架作者信息（[7b4057d](https://github.com/W1ndys/W1ndysBot-dev/commit/7b4057d75f59f79f4bbbdfc31b24288804a14e8d)）

## 2025-06-14

- **InviteTreeRecord**：优化群成员被移除时的邀请者踢出逻辑为异步并发，提高批量处理效率，去除主动确认消息步骤，处理逻辑更精简（[ac3afa6](https://github.com/W1ndys/W1ndysBot-dev/commit/ac3afa6)）
- **GroupBanWords**：增加消息文本预处理环节，自动去除标点、空白及换行，提高违禁词检测准确性（[988b96d](https://github.com/W1ndys/W1ndysBot-dev/commit/988b96d)）
- **GroupBanWords**：修复历史消息处理 bug，将检测历史消息数量调整为 15，优化撤回逻辑，增强日志记录（[b4cb9e0](https://github.com/W1ndys/W1ndysBot-dev/commit/b4cb9e0)）
- **GroupBanWords 模块**：增强群消息管理功能，支持历史消息请求及违规时自动获取历史消息，提升违规溯源能力（[82d2c64](https://github.com/W1ndys/W1ndysBot-dev/commit/82d2c64)）
- **message**：优化获取群历史消息函数的参数说明和默认值，完善返回值说明（[5f22d57](https://github.com/W1ndys/W1ndysBot-dev/commit/5f22d57)）
- **GroupHumanVerification**：修复自动扫描逻辑，确保类变量初始化，提升群用户验证效率，增加定时自动扫描功能（[f47c240](https://github.com/W1ndys/W1ndysBot-dev/commit/f47c240), [4250f10](https://github.com/W1ndys/W1ndysBot-dev/commit/4250f10), [01fbbce](https://github.com/W1ndys/W1ndysBot-dev/commit/01fbbce)）

## 2025-06-13

- **GroupHumanVerification**：优化群用户验证处理逻辑，增加异步任务处理以提升效率（[7f657d0](https://github.com/W1ndys/W1ndysBot-dev/commit/7f657d01294de5a1f37d77e10087076dce7ee6a9)）
- **GroupHumanVerification**：调整用户踢出和消息发送的暂停时间以释放控制权（[be1bf86](https://github.com/W1ndys/W1ndysBot-dev/commit/be1bf8660a289cbea4e9b33af8c53a526235bfb1)）
- **GroupHumanVerification**：在用户被踢出时增加短暂停顿以交出控制权（[fab32ea](https://github.com/W1ndys/W1ndysBot-dev/commit/fab32eaa5b5ea8a41bf1ea38f5a1ff1d784d054d)）
- **GroupBanWords**：更新违禁词检测返回格式，包含权重信息（[996204e](https://github.com/W1ndys/W1ndysBot-dev/commit/996204ec1c065caca0c34da5a314b10ac0cae9b2)）
- **EventHandler**：更新模块加载成功消息格式，调整换行符位置以提升可读性（[23dd3cb](https://github.com/W1ndys/W1ndysBot-dev/commit/23dd3cbb0f4dd7bd022d5eda1383623bd0c3010c)）
- **GroupBanWords**：更新违禁词报告格式，包含权重信息（[ba38056](https://github.com/W1ndys/W1ndysBot-dev/commit/ba38056b466981d0839c4aab3d2dfde765dd350c)）
- **GroupBanWords**：移除不必要的 data_manager 参数传递，并优化代码结构（[8fb7caf](https://github.com/W1ndys/W1ndysBot-dev/commit/8fb7caf2a43c506f3eaead3ce851595506db5193)）
- **GroupBanWords**：修复违禁词检测逻辑，调整权重判断条件，简化参数传递和优化 ForwardMessageHandler（[75ac199](https://github.com/W1ndys/W1ndysBot-dev/commit/75ac199e6b2d1f85e9e446d3eb894a49c8beb0bc)）
- **GroupNoticeHandler**：更新欢迎消息内容，简化用户验证流程说明（[fb62860](https://github.com/W1ndys/W1ndysBot-dev/commit/fb6286057aac3bf3c01445b19f31fbd2af1353b7)）

## 2025-06-12

- **GroupBanWords**：优化群违禁词复制为异步批处理，采用`asyncio.create_task`后台每批 20 条处理，提升大规模数据操作性能与主循环响应性，复制过程提供进度提示并移除未用常量导入（[add71bd1](https://github.com/W1ndys/W1ndysBot-dev/commit/add71bd1e2203eb8da1eb085b66b4ea42c0d3ee6)）
- **bot**：消息处理全面异步化，使用`asyncio.create_task`避免消息处理阻塞接收循环，提升 WebSocket 并发性能与整体稳定性（[1b02624](https://github.com/W1ndys/W1ndysBot-dev/commit/1b02624b6eaeb814dccb3cbc2745dbf29e990965)）
- **GroupBanWords**：抽离通用违禁词检测逻辑至`ban_words_utils.py`的`check_and_handle_ban_words`函数，两个消息处理器统一调用降低重复代码并提升后续扩展性，且`ForwardMessageHandler`中的`data_manager`延迟初始化（[e83787c](https://github.com/W1ndys/W1ndysBot-dev/commit/e83787cbe7f2461f35bfe913317958a91645564a)）
- **GroupBanWords**：违禁词监控功能新增对合并转发消息的解析与处理（[db45369](https://github.com/W1ndys/W1ndysBot-dev/commit/db453696fb15e7ee5437a52d2f7702506a0d349b)）
- **main.py**：增加`.env`文件存在性检查，不存在时提示并退出，提升配置友好性（[d000e82](https://github.com/W1ndys/W1ndysBot-dev/commit/d000e82ab857d27669d654d3f4bec244f3c0d4a0)）
- **online_detect.py**：增强机器人上线日志细节，输出在线状态、心跳间隔、机器人 ID 及管理员 ID，便于调试与监控（[e672d6d](https://github.com/W1ndys/W1ndysBot-dev/commit/e672d6d86c1d923f043d6c49d4da74d36b0bdfac)）
- **群人机验证**：扫描未验证用户前支持异步提示和 0.5 秒延时，优化交互体验，并同步应用于群内按需扫描（[92341b4](https://github.com/W1ndys/W1ndysBot-dev/commit/92341b4ce95aec1865f666ec58e7fec4aaaf6dc6)）

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
