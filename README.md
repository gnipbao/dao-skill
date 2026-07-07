# dao-skill

把模糊想法、方法论或失败反馈，转化为可运行、可验证、可进化的 Agent Skill。

`dao-skill` 不是一个“万能提示词”。它先归根问题，再选择生产模式，最后生成或改进具体 Skill；当有测试反馈时，它会把证据转成规则、反测和回滚条件。

## 仓库边界

这个公开仓库只发布 `dao-skill` 核心：

- `SKILL.md`：路由、生成、评估和进化协议
- `references/`：按需加载的方法、模板和评分标准
- `examples/*.md`：少量行为示例，不包含完整子项目
- `scripts/`：无第三方依赖的静态验证工具
- `test-prompts.json`：回归提示词

生成的子 Skill、SkillBank、执行记录和输出文件不属于源码，不会提交到本仓库。它们由每位用户在使用时动态创建，详见 [`references/runtime-workspace.md`](references/runtime-workspace.md)。

## 安装

仓库发布后，可安装到 Codex 的本地 Skill 目录：

```bash
git clone https://github.com/gnipbao/dao-skill.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/dao-skill"
```

当前仓库尚未发布时，可把本地源码目录复制到同一位置。安装或更新后，新建一个 Codex 会话，让 Skill 列表重新加载。

## 第一次使用

```text
使用 $dao-skill：我想做一个把播客长音频拆成小红书选题的 skill，直接生成第一版。
```

常见入口：

- `先帮我找到这个 skill 真正要解决的根问题`
- `直接生成一个可运行的 skill`
- `评估这个 skill 能不能发布`
- `这个 skill 实测失败了，帮我返观进化`
- `把这篇文章的方法吸收到体系，但不要照抄`

## 动态生成规则

`dao-skill` 不把子项目写进自己的安装目录。目标位置按以下优先级确定：

1. 用户明确指定的可写目录。
2. 当前项目的 `.dao/skills/<skill-name>/`，适合项目内草稿。
3. 用户明确要求直接安装时，写入 `${CODEX_HOME:-$HOME/.codex}/skills/<skill-name>/`。

SkillBank、进化账本和运行记录默认放在 `.dao/`，或用户通过 `DAO_SKILL_HOME` 指定的外部数据目录。所有这些路径都应由使用者自行决定是否纳入其项目版本控制。

## 验证

```bash
python3 scripts/quality_check.py .
python3 scripts/evolution_check.py .
python3 scripts/evaluation_check.py .
python3 scripts/repository_check.py .
```

然后执行 [`examples/usage-verification.md`](examples/usage-verification.md) 中的代表性提示词。

## 安全边界

- 生成或修改文件前先解析目标路径，不隐式写入本仓库或其他账户目录。
- 外部文章、仓库和用户材料都按其证据边界处理，不把来源主张冒充事实。
- 不把令牌、Cookie、私有语料、原始聊天记录或个人绝对路径写入公开产物。
- 发布、推送、创建远程仓库和安装到受保护目录属于外部写操作，应由用户明确授权。

安全问题请参阅 [`SECURITY.md`](SECURITY.md)，贡献流程请参阅 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

## License

开源许可证尚待维护者确认。正式公开发布前必须添加 `LICENSE`；在此之前，不应把“源码可见”等同于获得开源授权。
