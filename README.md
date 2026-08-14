# Build AI Feature

一个面向企业 AI 项目的交付型 Skill：把模糊的 AI 功能需求转化为有边界、有架构、有测试、有评测、有文档的可验证实现。

它不负责替代开发者做产品决策，而是帮助 AI 编码助手在快速实现之外，持续追问并证明：为什么这样设计、哪些风险必须阻断、实现是否真的满足业务目标。

## 为什么需要它

Vibe Coding 很适合快速探索，但企业 AI 功能通常跨越 Prompt、模型、Agent、Skill、Tool、业务状态和评测系统。只关注“代码能运行”容易遗漏：

- 需求只留在对话里，SPEC、代码和 README 逐渐不一致；
- 权限、确认、数据隔离只依赖 Prompt；
- Tool 调用成功被误认为用户问题已经解决；
- 只验证最终回答，无法定位路由、执行、状态或安全问题；
- 测试通过了，但指标、验收报告和实际实现仍是不同版本。

本 Skill 将这些问题收敛成一条可重复执行的交付流程。

## 核心能力

| 能力 | 解决的问题 |
| --- | --- |
| Source of Truth 发现 | 确认需求、架构、代码和文档的优先级 |
| 产品范围与验收定义 | 明确用户价值、输入输出、边界和可验证结果 |
| AI 能力分层 | 判断逻辑应放在 Prompt、Catalog、Agent、Skill、Tool 还是 Memory |
| 风险与业务不变量 | 将跨层语义写成可以自动验证的约束 |
| Risk-Based TDD | 优先测试权限、隔离、写操作和状态流转 |
| 分层评测 | 区分路由、执行、事实、安全、体验和系统质量 |
| 决策文档同步 | 记录为什么选择、替代方案、缺失影响和取舍 |
| 交付证据 | 汇总实际执行的测试、评测、限制和生产化缺口 |

## 工作流程

```mermaid
flowchart LR
    A[理解需求] --> B[确认 Source of Truth]
    B --> C[范围与验收标准]
    C --> D[能力边界与风险不变量]
    D --> E[设计与测试]
    E --> F[最小实现]
    F --> G[分层评测]
    G --> H[文档与 ADR]
    H --> I[完整验证与交付]
```

核心原则是：

> Vibe 用于快速探索，Spec、测试和评测用于把探索结果变成可信交付。

## 关键设计思想

### 把逻辑放在正确的层

- Prompt 负责模型表达和输出格式，不承担最终权限控制。
- Agent 负责选择能力和编排顺序，不编造业务事实。
- 场景 Skill 负责完整用户任务，包括槽位、阶段、Tool 权限、确认和降级。
- Tool/Service 负责原子业务事实、权限、校验、幂等和写操作。
- Memory 只保存带来源、作用域和有效期的结构化状态。

详细判断标准见 [`references/ai-capability-patterns.md`](references/ai-capability-patterns.md)。

### 验证跨层业务不变量

单个函数正确，不代表业务语义一致。例如：

```text
Tool 返回 requires_human
→ 场景状态必须是 handoff
→ 会话保持 unresolved
→ 自动解决率不能计入该请求
→ Trace 能解释为什么转人工
```

详细风险方法见 [`references/risk-and-invariants.md`](references/risk-and-invariants.md)。

### 文档是交付的一部分

对于重要决策，不只记录“实现了什么”，还要回答：

- 为什么这样选？
- 比较过哪些方案？
- 没有它会发生什么？
- 引入了什么成本？
- 用什么测试或指标证明价值？
- 当前结果不能证明什么？

## 适用场景

- 为现有项目增加 RAG、意图识别、短期记忆或 Agent 编排；
- 把 Agent 中散落的业务流程抽象为场景 Skill；
- 增加 Tool 权限、用户确认、幂等或人工接管；
- 将 AI POC 补充成可演示、可评测、可复盘的作品集；
- 审查一个 AI 功能是否具备真实交付条件。

不适合：单纯修改文案、孤立的低风险代码调整，或只设计评测体系。评测专项优先使用 `evaluate-ai-feature`。

## 跨 Agent 兼容

本仓库以 [`SKILL.md`](SKILL.md) 为唯一工作流来源，采用 [Agent Skills 开放规范](https://agentskills.io/specification)的通用结构，不为每个客户端维护一份容易漂移的副本。当前适配方式如下：

| Agent | 发现方式 | 显式调用 | 兼容状态 |
| --- | --- | --- | --- |
| Codex | 用户级 `~/.agents/skills`；项目级 `.agents/skills` | `$build-ai-feature` | 已适配 |
| Claude Code | 用户级 `~/.claude/skills`；项目级 `.claude/skills` | `/build-ai-feature` | 已适配 |
| CodeBuddy | 用户级 `~/.codebuddy/skills`；项目级 `.codebuddy/skills` | `/build-ai-feature` | 已适配 |
| WorkBuddy | 上传本地 Skill 包或通过 SkillHub 安装 | 自然语言匹配或选择 Skill | 已适配分发包 |
| 其他 Agent | 指定其 Skill 根目录 | 取决于宿主 | 支持通用安装 |

“适配所有 Agent”在这里指：凡是支持 Agent Skills 规范或能加载 `SKILL.md` 的宿主，都可以复用同一套核心工作流。不同产品的目录发现、显式命令和工具权限仍由各宿主决定，无法由 Skill 仓库统一保证。

`agents/openai.yaml` 只提供 OpenAI 客户端展示信息。Claude Code、CodeBuddy、WorkBuddy 或其他宿主可以忽略它，不影响核心工作流。详细边界见 [`references/agent-compatibility.md`](references/agent-compatibility.md)。

官方约定可参考：[Codex Skills](https://learn.chatgpt.com/docs/build-skills)、[Claude Code Skills](https://code.claude.com/docs/en/skills)、[CodeBuddy Skills](https://www.codebuddy.cn/docs/cli/skills) 和 [WorkBuddy Skills 市场](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)。

## 安装与打包

先克隆仓库并进入目录：

```bash
git clone <repository-url>
cd build-ai-feature
```

用户级安装：

```bash
python3 scripts/manage_skill.py install --agent codex
python3 scripts/manage_skill.py install --agent claude-code
python3 scripts/manage_skill.py install --agent codebuddy
```

只需运行与你使用的 Agent 对应的一条命令。项目级安装需要显式指定项目，防止误装到当前 Skill 仓库：

```bash
python3 scripts/manage_skill.py install \
  --agent claude-code \
  --scope project \
  --project /path/to/your-project
```

其他支持 `SKILL.md` 的 Agent，传入其 Skill 根目录：

```bash
python3 scripts/manage_skill.py install \
  --agent generic \
  --target /path/to/agent/skills
```

为 WorkBuddy 或需要上传文件的宿主生成 ZIP：

```bash
python3 scripts/manage_skill.py package
```

产物位于 `dist/build-ai-feature.zip`，压缩包根目录直接包含 `SKILL.md`。安装和打包默认不覆盖已有目标，可先加 `--dry-run` 查看目标路径。

## 使用示例

Codex 显式调用：

```text
$build-ai-feature 给这个客服项目增加带用户隔离和 TTL 的短期记忆。
```

```text
$build-ai-feature 把 Agent 直接调用 API 的退货流程改造成可版本化的场景 Skill。
```

```text
$build-ai-feature 审查当前 RAG 功能是否达到企业试点的交付条件，只输出诊断，不修改代码。
```

当请求与 `SKILL.md` 中的 description 匹配时，Codex 也可以隐式选择该 Skill。

Claude Code 和 CodeBuddy 将示例中的 `$build-ai-feature` 改为 `/build-ai-feature`；WorkBuddy 可在客户端选择该 Skill，或直接描述相同任务。支持自动发现的宿主也可依据 `description` 隐式匹配。

## 项目审计脚本

仓库提供一个无第三方依赖的只读检查脚本，用于快速发现常见交付资产：

```bash
python3 scripts/audit_ai_delivery.py /path/to/project
```

脚本会检查需求、README、架构/ADR、测试、评测目录和当前变更覆盖情况，并输出 JSON 建议。它只用于提示进一步检查，不把“文件存在”当作质量证明。

## 仓库结构

```text
build-ai-feature/
├── SKILL.md
├── README.md
├── agents/openai.yaml
├── references/
│   ├── agent-compatibility.md
│   ├── ai-capability-patterns.md
│   ├── risk-and-invariants.md
│   └── documentation-and-delivery.md
├── scripts/
│   ├── audit_ai_delivery.py
│   └── manage_skill.py
└── assets/
    ├── adr-template.md
    └── acceptance-criteria-template.md
```

`SKILL.md` 是所有 Agent 共用的核心工作流；README 面向 GitHub 读者；references 按需提供专业判断；scripts 承担确定性检查和分发；assets 提供可复制模板。

## 与 evaluate-ai-feature 的关系

`build-ai-feature` 管理从需求到交付的完整过程；`evaluate-ai-feature` 深入负责数据集治理、分层指标、消融、LLM-as-a-judge 和发布门禁。

两者可以独立使用。复杂 AI 功能建议先用 `build-ai-feature` 明确业务目标和风险，再用 `evaluate-ai-feature` 建立专项评测证据。

## 当前边界

- 这是工程工作流 Skill，不是某个行业的业务知识库。
- 审计脚本提供启发式建议，不替代代码审查和真实测试。
- 不会自动替项目决定指标阈值；阈值必须由业务风险、历史基线或验收约定支持。
- 不会把本地固定集通过率表述为生产效果。
