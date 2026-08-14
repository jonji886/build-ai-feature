# Agent 兼容与分发

## 兼容原则

以仓库根目录的 `SKILL.md` 作为唯一事实来源，并遵循 Agent Skills 开放规范的最小公共能力：YAML frontmatter、Markdown 指令，以及可选的 `scripts/`、`references/`、`assets/`。不要为不同 Agent 复制并维护多份工作流。

宿主可以有不同的发现目录、调用语法和工具能力。执行时应将用户意图与本 Skill 工作流绑定，而不是依赖某个产品专属命令。宿主不支持某项工具时，使用等价能力；不存在安全等价方案时，明确报告限制，不绕过权限。

## 已验证的宿主约定

| 宿主 | 用户级目录 | 项目级目录 | 常见显式调用 |
| --- | --- | --- | --- |
| Codex | `~/.agents/skills/<name>` | `<project>/.agents/skills/<name>` | `$<name>` |
| Claude Code | `~/.claude/skills/<name>` | `<project>/.claude/skills/<name>` | `/<name>` |
| CodeBuddy | `~/.codebuddy/skills/<name>` | `<project>/.codebuddy/skills/<name>` | `/<name>` |
| WorkBuddy | 通过客户端上传本地 Skill 包或 SkillHub 安装 | 由客户端管理 | 自然语言匹配或选择 Skill |
| 其他 Agent | 查阅宿主的 Skill 根目录 | 查阅宿主文档 | 由宿主决定 |

目录和调用方式属于宿主能力，不写进核心工作流。对其他支持 `SKILL.md` 或 Agent Skills 规范的 Agent，使用 `scripts/manage_skill.py install --agent generic --target <skills-root>` 安装。

## 可选元数据

`agents/openai.yaml` 只增强 OpenAI 客户端中的名称、描述和默认提示，不承载业务规则。忽略该文件的宿主仍应能仅凭 `SKILL.md` 与资源目录执行完整工作流；删除它会损失 OpenAI 展示配置，但不会改变核心方法。

## 可移植打包

运行 `python3 scripts/manage_skill.py package`，生成 `dist/<name>.zip`。压缩包根目录直接包含 `SKILL.md` 和配套资源，便于 WorkBuddy 上传或其他宿主导入。若某个宿主只接受目录，则将压缩包解压到其 Skill 根目录下的 `<name>/`。

## 兼容性门禁

- `SKILL.md` 的 `name` 与目录名保持一致。
- 核心指令不引用某个宿主独有的工具名。
- 相对路径从 Skill 根目录解析。
- Python 脚本仅使用标准库，并提供清晰的输入输出和失败状态。
- 宿主专属元数据保持可选，不能成为运行前提。
- 新增资源后，同时验证安装副本与 ZIP 中的路径。
