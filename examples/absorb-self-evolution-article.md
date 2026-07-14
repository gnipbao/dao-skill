# Example: Absorb A Self-Evolution Article

User:

```md
研究下面这段用户提供的文章摘要，然后吸收到 dao-skill 的体系里，变成一个可以自主进化的系统。

摘要：文章比较了 SkillRL、AutoSkill、MemSkill 与 SkillClaw，认为执行经验应被压缩成可检索、可合并、可版本化的 Skill，并在部署前通过失败回放和回滚门禁。这里只提供摘要，没有提供论文原文或完整仓库实现。
```

Expected dao-skill behavior:

```md
## 道.skill 自化吸收
来源：用户粘贴的《【Agent Skills洞察与实践】08- 如何实现Skills的自进化》
证据边界：二手综述材料；未单独核验论文与仓库，因此只吸收机制，不把实验数字写成全局事实。

核心机制：
1. 把经验压缩成技能，不保存原始噪声。
2. 候选技能必须先检索相似资产，再决定新增、合并或丢弃。
3. 成功轨迹提供不变量，失败轨迹提供修复靶点。
4. 采用保守编辑、版本化更新、验证门禁和回滚。

新增/合并/丢弃：
新增：自化吸收模式与自进化参考协议。
合并：返观进化协议加入候选管理、保守编辑、验证与回滚。
丢弃：不把论文指标、仓库实现细节、整篇正文存入全局提示。

已更新文件：
- SKILL.md
- references/self-evolving-skill-system.md
- references/evolution-protocol.md

验证方式：
- python3 scripts/quality_check.py . --profile dao
- python3 scripts/evolution_check.py .
- 用下一条反测做 dry-run，并明确其证据仅为 E2 provisional

回滚条件：
- 新规则导致每次反馈都新增 Skill、绕过 nearest-asset retrieval，或在无验证时自动部署时，回滚本次规则并将证据标记为 quarantined。

下一轮反测：
让 dao-skill 处理一篇新的外部方法文章，检查它是否更新规则/参考/反测，而不是只写摘要。
```

Anti-example:

```md
这篇文章说技能可以自我进化。以后我会学习用户反馈并持续优化。
```

Why this fails:

- no source boundary
- no durable file or rule change
- no create/merge/discard decision
- no validation or retest
- no rollback condition
