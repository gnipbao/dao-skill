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
  <img alt="Python 3.9+" src="https://img.shields.io/badge/Python-3.9%2B-334155.svg" />
</p>

## 15 秒看懂道 · Skill

https://github.com/user-attachments/assets/6fffc9a3-e69f-41ab-9347-7ec9e0a0866a

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
| 评估 / 优化 | 不确定现有 Skill 是否可靠、如何改好或能否发布 | Trust Gate、证据化评分、最小补丁、P0/P1/P2 修复 |
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

需要 Python 3.9+，安装器只使用标准库。先克隆源码到任意维护目录：

```bash
git clone https://github.com/gnipbao/dao-skill.git
cd dao-skill
```

先预览安装清单，再原子安装到 `${CODEX_HOME:-$HOME/.codex}/skills/dao-skill`：

```bash
python3 scripts/install.py --dry-run
python3 scripts/install.py
```

Windows PowerShell 使用 `py -3` 代替 `python3`。如目标已存在，安装器会要求显式使用 `--force`；默认安装的旧版本会保存在 `${CODEX_HOME:-$HOME/.codex}/backups/dao-skill/default/<timestamp>/`，不会留在可发现的 `skills/` 目录里。

更新：

```bash
git pull --ff-only
python3 scripts/run_checks.py
python3 scripts/install.py --dry-run
python3 scripts/install.py --force
```

需要回滚（包括首次从旧版升级）时，使用安装器输出的真实备份路径：

```bash
python3 scripts/install.py --restore-backup /path/from/installer/output --dry-run
python3 scripts/install.py --restore-backup /path/from/installer/output
```

自定义安装位置必须在安装、更新和回滚时重复传入同一个 `--target`；可用 `--state-dir` 把暂存与备份固定到另一个非 Skill 扫描目录。安装或更新后，新建 Codex 会话，让 Skill 列表重新加载。

```bash
python3 scripts/install.py \
  --target /path/to/custom-skills/dao-skill \
  --state-dir /path/to/private-installer-state \
  --dry-run
```

`main` 会持续演进；需要完全可复现的安装时，请在安装前检出一个已验证的 tag 或 commit SHA。

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

优化已有 Skill：

```text
使用 $dao-skill：先审计当前 skill，再直接优化文件并验证；保留已有有效行为，不要用增加篇幅冒充进步。
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
│   ├── install.py              # 安全、可回滚的全局安装器
│   └── run_checks.py           # 单一完整验证入口
├── test-prompts.json           # 回归提示词
├── SECURITY.md
├── CONTRIBUTING.md
└── LICENSE
```

本仓库刻意不包含完整子 Skill 项目。用户使用时动态创建，维护者也可以把成熟子 Skill 放到独立仓库。

## 本地验证

源码仓库运行一条命令即可完成结构、进化、评分、静态行为契约、发布边界、安装器和验证器回归检查：

```bash
python3 scripts/run_checks.py
```

安装后的 Skill 也可以运行同一命令；它会自动跳过只适用于 Git 源码仓库的发布检查。静态行为契约只验证测试夹具与控制规则是否齐全，不等同于真实模型回放；没有执行记录时，证据仍应标为 E1/E2。

CI 在 Linux、macOS 和 Windows 上运行同一套标准库检查。

## 设计原则

- **哲学必须落地**：隐喻必须变成行为规则。
- **文件优先**：用户要求生成时，不能只给计划或草稿说明。
- **证据优先**：没有运行证据，就不宣称已验证或达到标杆级。
- **优化有停止条件**：“最好”指当前范围内没有已知 P0/P1 缺陷、旧成功行为仍成立、剩余不确定性已披露，不指最长或功能最多。
- **Trust 是硬门槛**：高分不能抵消权限、隐私或依赖风险。
- **先检索再新增**：资产只决定 create、merge 或 discard；部署状态单独记录 accepted、provisional、quarantined 或 rejected。
- **进化必须可回滚**：每次改变都要有反测、通过信号和回滚条件。
- **核心与运行时分离**：用户生成数据不污染公开源码。

## 安全与贡献

- 阅读 [`SECURITY.md`](SECURITY.md) 了解文件写入、私有材料和外部输入边界。
- 阅读 [`CONTRIBUTING.md`](CONTRIBUTING.md) 了解核心仓库的贡献范围。
- 不要提交 Token、Cookie、私有语料、原始聊天记录、本机绝对路径或生成输出。
- 创建远程仓库、发布、推送及写入受保护目录前，应获得用户明确授权。

## License

[MIT](LICENSE) © 2026 [gnipbao](https://github.com/gnipbao)
