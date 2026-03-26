# requirements-elicitation Skill

一个用于“半结构化需求访谈”的可复用 Skill。它会在多轮对话中持续维护访谈框架，动态补全信息、识别冲突并在完成时输出结构化需求总结。

## 目录结构

```text
.
├── SKILL.md
├── assets/
│   ├── interview_framework_schema.json
│   └── requirements_report_format.md
├── references/
│   ├── checkpoints.md
│   ├── conflict_resolution.md
│   ├── fill_framework.md
│   ├── generate_speak.md
│   ├── intent_routing.md
│   ├── maintain_framework.md
│   ├── select_current_topic.md
│   ├── state_cleanup.md
│   ├── state_lifecycle.md
│   ├── state_management.md
│   ├── state_storage_rules.md
│   └── topic_dependency_map.md
└── examples/
    ├── contradiction_resolution_example.md
    ├── fill_framework_example.md
    ├── generate_speak_example.md
    ├── intent_routing_example.md
    ├── modify_framework_example.md
    ├── new_framework_example.md
    ├── select_current_topic_example.md
    └── summarize_example.md
```

## Skill 能力

- 通过意图识别决定当前输入是补槽、澄清、切题还是结构更新信号
- 支持初始化与动态维护访谈框架（增删主题/字段、合并拆分主题）
- 在填充信息时保留“已确认/待确认/冲突”状态
- 自动检测前后矛盾并优先发起澄清
- 在完成条件满足后输出最终框架与结构化需求报告

## 使用方式

1. 将整个目录作为一个 Skill 包上传或放入你的 Skill 仓库。
2. 确保运行环境能读取 `SKILL.md` 及其引用的 `assets/`、`references/`、`examples/` 文件。
3. 在对话中给出一个产品想法或功能设想，Skill 会自动进入访谈流程：
   - 检查当前阶段
   - 识别意图并路由
   - 维护框架结构
   - 填充信息并处理冲突
   - 选择当前主题并生成下一轮问题
4. 当完成条件达成后，Skill 会停止追问并输出结构化总结。

## 打包与发布建议

参考社区常见 Skill 仓库风格，保持以下原则：

- 仓库根目录保留 `SKILL.md` 作为唯一入口
- 规则说明、示例、资产文件分目录管理，避免全部写入单文件
- 版本迭代时优先保持路径稳定，避免破坏已有引用
- 发布时按目录原样上传，不要只传 `SKILL.md`

推荐使用 zip 包分发：

1. 在仓库根目录打包整个目录。
2. 解压后应直接看到 `SKILL.md` 与三个子目录。
3. 在目标平台导入后先做一次最小用例验证。

## 最小示例

用户输入：

```text
我们要做一个校园二手交易小程序，先在校内试点。
```

Skill 输出行为（示意）：

- 识别产品类型与范围
- 初始化访谈框架
- 先追问用户、交易流程、履约与风控约束
- 在信息充分后生成结构化需求摘要

## 许可证

当前 `SKILL.md` 中声明为 `Proprietary`。如需开源发布，请按你的实际授权策略调整。
