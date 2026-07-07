<p align="center">
  <img src="assets/dao-skill-banner.png" alt="道 · Skill — 老子骑青牛" width="100%" />
</p>

<h1 align="center">道 · Skill</h1>

<p align="center">
  <strong>先归根，再分化；先明道，再造物。</strong><br />
  从混沌需求出发，生成可运行、可验证、可进化的 Agent Skill。
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-0f766e.svg" /></a>
  <img alt="Python: standard library" src="https://img.shields.io/badge/Python-stdlib_only-334155.svg" />
  <img alt="Status: open source ready" src="https://img.shields.io/badge/Status-open_source_ready-b7791f.svg" />
</p>

---

`dao-skill` 是一个 Skill 元设计器。它不直接扮演所有业务专家，而是帮你找到真正的问题、选择正确的 Skill 形态、生成具体产物，并用证据持续改进。

> 道生一，一生二，二生三，三生万物。
> 一个根问题，可以生出一套稳定工作流，也可以生出一个完整 Skill 家族。

## 它能做什么

| 模式 | 解决的问题 | 典型产物 |
| --- | --- | --- |
| 归根 | 想法很模糊，不知道真正要解决什么 | 根问题、第一性原理、最小下一步 |
| 设计 | 方向明确，但 Skill 形态尚未确定 | 定位、流程、边界、目录结构 |
| 生成 | 需要直接写出可运行文件 | `SKILL.md`、references、examples、scripts |
| 评估 | 不确定现有 Skill 是否可靠、能否发布 | Trust Gate、100 分评分、P0/P1/P2 修复 |
| 返观 | 实测结果不对，不能只修表面症状 | 失败复盘、保守补丁、反测与回滚 |
| 自化 | 想把文章、仓库或执行经验吸收到系统 | create / merge / discard 决策与持久规则 |

## 核心工作流

```text
混沌需求
   ↓
道：理解真实关切
   ↓
一：归结根问题
   ↓
二：识别核心张力
   ↓
三：建立天 / 地 / 人结构
   ↓
器：选择生产模式
   ↓
万物：生成可运行产物
   ↓
验证 → 反馈 → 返观进化
```

这里的道家语言不是装饰。每个概念都必须落成决策规则、执行步骤、输出结构或验证标准。

## 安装

仓库发布到 GitHub 后，克隆到 Codex 的本地 Skill 目录：

```bash
git clone https://github.com/gnipbao/dao-skill.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/dao-skill"
```

如果已克隆到其他目录，也可以复制源码：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R /path/to/dao-skill "${CODEX_HOME:-$HOME/.codex}/skills/dao-skill"
```

安装或更新后，新建一个 Codex 会话，让 Skill 列表重新加载。

## 第一次调用

从一个模糊想法开始：

```text
使用 $dao-skill：我想做一个帮创业者判断产品方向的 skill，先帮我归根。
```

直接生成第一版：

```text
使用 $dao-skill：我想做一个把播客长音频拆成小红书选题的 skill，直接生成第一版。
```

评估已有 Skill：

```text
使用 $dao-skill：评估这个 skill 能不能发布。先过 Trust Gate，再给证据化评分。
```

从失败中进化：

```text
使用 $dao-skill：这个 skill 实测只会堆模板，没有帮我做选择。请返观根因并更新它。
```

更多代表性输入见 [`examples/usage-verification.md`](examples/usage-verification.md)。

## 仓库边界：子 Skill 动态生成

公开仓库只发布 `dao-skill` 核心。生成的子 Skill、SkillBank、执行记录、隔离证据和输出文件都属于使用者，不随源码分发。

目标位置按以下优先级确定：

1. 用户明确指定的可写目录。
2. 当前项目的 `.dao/skills/<skill-name>/`，适合项目内草稿。
3. 用户明确要求直接安装时，写入 `${CODEX_HOME:-$HOME/.codex}/skills/<skill-name>/`。

SkillBank 和进化状态默认放在项目 `.dao/`，也可通过 `DAO_SKILL_HOME` 指向仓库外的用户数据目录。完整规则见 [`references/runtime-workspace.md`](references/runtime-workspace.md)。

## 仓库结构

```text
dao-skill/
├── SKILL.md                    # 核心路由与执行协议
├── agents/openai.yaml          # Codex 展示与默认调用配置
├── references/                 # 按需加载的框架、模板与标准
├── examples/*.md               # 行为示例，不包含完整子项目
├── scripts/                    # 标准库验证工具
├── test-prompts.json           # 回归提示词
├── SECURITY.md
├── CONTRIBUTING.md
└── LICENSE
```

本仓库刻意不包含完整子 Skill 项目。用户使用时动态创建，维护者也可以把成熟子 Skill 放到独立仓库。

## 本地验证

所有检查只依赖 Python 标准库：

```bash
python3 scripts/quality_check.py .
python3 scripts/evolution_check.py .
python3 scripts/evaluation_check.py .
python3 scripts/repository_check.py . --strict-license
```

检查内容包括：Skill 结构、进化协议、评分体系、私有路径/密钥风险、子项目与运行时文件是否越过发布边界。

## 设计原则

- **哲学必须落地**：隐喻必须变成行为规则。
- **文件优先**：用户要求生成时，不能只给计划或草稿说明。
- **证据优先**：没有运行证据，就不宣称已验证或达到标杆级。
- **Trust 是硬门槛**：高分不能抵消权限、隐私或依赖风险。
- **先检索再新增**：新经验先决定 create、merge、discard 或 quarantine。
- **进化必须可回滚**：每次改变都要有反测、通过信号和回滚条件。
- **核心与运行时分离**：用户生成数据不污染公开源码。

## 安全与贡献

- 阅读 [`SECURITY.md`](SECURITY.md) 了解文件写入、私有材料和外部输入边界。
- 阅读 [`CONTRIBUTING.md`](CONTRIBUTING.md) 了解核心仓库的贡献范围。
- 不要提交 Token、Cookie、私有语料、原始聊天记录、本机绝对路径或生成输出。
- 创建远程仓库、发布、推送及写入受保护目录前，应获得用户明确授权。

## License

[MIT](LICENSE) © 2026 [gnipbao](https://github.com/gnipbao)
