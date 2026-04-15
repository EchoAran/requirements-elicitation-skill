# Requirements Elicitation Skill

一个用于**半结构化需求访谈**的 Agent Skill。  
它可以把“模糊想法”逐轮转成结构化需求框架，并在完成时产出可落地的需求总结。

## 这个 Skill 能做什么

- 用多轮访谈方式逐步澄清产品目标、用户、流程、功能、约束与优先级
- 维护可追踪的访谈框架（带证据与置信度）
- 在访谈过程中动态增删/调整话题
- 处理矛盾信息并优先澄清
- 最终输出：
  - 完整访谈框架（JSON）
  - 结构化需求总结报告（Markdown）

## 仓库结构

```text
.
├── SKILL.md                        # Skill 入口与主流程
├── assets/
│   ├── interview_framework_schema.json
│   └── requirements_report_format.md
├── references/                     # 各步骤规则
│   ├── checkpoints.md
│   ├── maintain_framework.md
│   ├── fill_framework.md
│   ├── select_current_topic.md
│   ├── generate_speak.md
│   ├── intent_routing.md
│   ├── topic_dependency_map.md
│   ├── conflict_resolution.md
│   └── state_*.md
├── scripts/
│   ├── commit_state.py             # 事务式状态提交（tmp + checkpoint + commit.json）
│   ├── validate_state.py           # 状态文件与跨文件一致性校验
│   ├── check_state_drift.py        # schema drift 检查与迁移
│   ├── security_scan_state.py      # 状态文件敏感信息扫描
│   └── cleanup_sessions.py         # 两阶段归档/删除清理
└── examples/                       # 输入输出样例
    ├── new_framework_example.md
    ├── fill_framework_example.md
    ├── modify_framework_example.md
    ├── select_current_topic_example.md
    ├── generate_speak_example.md
    ├── contradiction_resolution_example.md
    ├── intent_routing_example.md
    ├── summarize_example.md
    ├── frequent_topic_switch_example.md
    ├── refusal_to_answer_example.md
    ├── conflicting_priorities_example.md
    └── goal_without_workflow_example.md
```

## 工作方式（核心执行链路）

每轮对话按以下步骤运行：

1. 加载会话状态  
2. 判断阶段（start / runtime / complete）  
3. 意图分类与产品类型路由  
4. 维护访谈框架结构  
5. 填充新信息到 slots  
6. 检测并处理矛盾  
7. 选择下一话题  
8. 生成下一轮提问  
9. 持久化状态  

完成条件满足后，输出最终框架与总结报告，并清理会话状态。

补充说明：

- 已支持更细粒度意图分类（含约束声明、优先级表达、例外场景）
- 已支持更广的产品类型起始路由（含 B2B SaaS、AI Copilot、教育、平台工具、数据分析、IoT）
- 完成判定采用“清单 + 分数阈值（coverage/convergence/estimated_completion）”
- 证据模型支持多条 evidence 链路，便于追溯

## 如何使用

## 1) 克隆仓库

```bash
git clone https://github.com/EchoAran/requirements-elicitation-skill.git
cd requirements-elicitation-skill
```

## 2) 作为 Skill 挂载

把此目录作为一个 Skill 目录提供给你的 Agent 运行环境（需支持读取 `SKILL.md` 与同级资源文件）。

关键点：

- Agent 先读取 `SKILL.md` 的 metadata 做发现与触发
- 命中后加载 `SKILL.md` 主体流程
- 再按需读取 `references/`、`assets/`、`examples/` 中文件

## 3) 发起访谈

在对话中给出一个初始需求，例如：

- “我想做一个校园二手交易 App，请帮我做需求访谈。”
- “我们要做企业内部审批工具，帮我澄清第一版需求。”

之后按 Skill 的提问逐轮回答即可。

## 输入与输出

### 输入

- 用户自然语言需求描述（可模糊、可分阶段补充）

### 输出

- 运行中：单轮聚焦问题 + 必要确认
- 完成时：
  - `final_interview_framework`（结构化 JSON）
  - `requirements_summary_report`（按模板输出的 Markdown 报告）

## 可定制项

- 话题策略：`references/maintain_framework.md`
- 选题路由：`references/select_current_topic.md` + `references/topic_dependency_map.md`
- 填充与证据规则：`references/fill_framework.md`
- 矛盾处理：`references/conflict_resolution.md`
- 完成判定：`references/checkpoints.md`
- 总结模板：`assets/requirements_report_format.md`

## 状态管理

默认使用文件状态持久化，目录约定见：

- `references/state_management.md`
- `references/state_storage_rules.md`
- `references/state_lifecycle.md`
- `references/state_cleanup.md`

补充状态规范：

- 事务提交：先写 `state/temp/{session_id}` 三个 tmp，再统一替换正式文件
- 提交锚点：每次成功提交写 `commit.json`（含 hash 与版本）
- 快照恢复：写入前创建 `checkpoints/v{n}`，默认保留最近 3~5 个
- 两阶段回收：完成后先 `closed`，再按策略归档和延迟删除
- 幂等写入：每轮使用稳定 `turn_id`，避免 Step 8 重试导致重复追加

## 脚本入口

```bash
python scripts/validate_state.py --state-root state --session-id <SESSION_ID>
python scripts/check_state_drift.py --state-root state --session-id <SESSION_ID> --migrate
python scripts/security_scan_state.py --state-root state
python scripts/cleanup_sessions.py --state-root state --archive-days 30 --delete-days 90
```

## 适用场景

- 0→1 产品探索
- 模糊需求澄清
- PRD 前置访谈
- 跨角色需求对齐（产品/业务/研发/运营）

## License

Proprietary（见 `SKILL.md` frontmatter）。
