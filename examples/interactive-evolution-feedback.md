# Example: Interactive Evolution Feedback

User:

```md
[$dao-skill] 这个生成的 skill 不好用。
```

Expected dao-skill behavior:

```md
我先把这个反馈变成可进化证据。你不用填模板，简单回答这 2 个就行：

1. 哪个 skill 或输出不好用，它实际哪里让你卡住？
2. 你希望它下次怎么做才算好用？
```

User:

```md
xhs-title-skill。它只给了很多标题模板，但没有判断我的内容适合哪个公式。我希望它先诊断内容，再推荐公式。
```

Expected next step:

```md
## 道.skill 返观
用户反馈：xhs-title-skill 只堆标题模板，没有做公式选择诊断。
交互式追问：已补齐关键证据，无需继续追问。
表层失败：输出有数量但没有决策。
根因失败：dao-skill 把“标题公式工具”误生成为模板库，没有编码选择标准。
dao-skill 自身缺口：生成公式类工具时缺少“诊断入口 + 选择准则 + 反测 prompt”。
新增规则：以后生成公式/模板类 skill，必须先定义选择条件，再输出候选。
文件更新计划：更新子 skill；必要时更新 dao-skill 的生产模式或示例。
验证方式：用一篇真实内容测试是否先诊断再推荐。
回滚条件：如果新增诊断步骤让明确指定公式的请求也被强制追问，回滚该路由并保留失败样本继续校准。
```

Anti-example:

```md
请按以下模板填写：失败对象、原始需求、实际表现、理想表现、失败类型、证据……
```

Why this fails:

- shifts the structuring work onto the user
- blocks evolution when the user only has a fuzzy dissatisfaction signal
- violates dao-skill's role as a root-finding meta skill
