# Example: Evaluate Existing Skill

User:

> 帮我看看这个 skill 能不能发布。

Dao response shape:

```md
## 道.skill 评估
总分：76/100
数值等级：MVP
最终判定：结构估分，尚不能确认可发布
评估模式：E1 structural
评分置信度：低

### Trust Gate
权限范围：N/A；证据：当前 skill 不调用工具。
敏感数据：CONDITIONAL；证据：要求用户提供材料，但未说明隐私处理。
输入与动作安全：N/A；证据：只生成文本，不执行外部动作。
依赖与来源：UNKNOWN；证据：引用了外部方法但没有来源清单。
环境适配：PASS；证据：无外部运行时依赖。
门禁结论：评估不完整；发布前必须补齐必要来源和隐私说明。

### 100 分评分
根问题与适用性：12/15；证据：目标和触发清楚，非目标不足。
流程可靠性：14/20；证据：有明确流程，但缺少失败时如何追问或停止；E1 上限适用。
结果有效性：14/20；证据：输出模板可复制，但没有真实任务运行记录。
边界与可信披露：7/10；证据：提到材料不足，未说明隐私和来源限制。
规范与维护性：9/10；证据：说明、模板和 references 组织清楚。
组合与交接能力：9/10；证据：有明确输入输出契约和交接规则。
证据与验证闭环：7/10；证据：包含回归 prompts、明确通过标准和记录格式，但没有 old-vs-new 或独立评估的实际结果。
可进化性：4/5；证据：反馈可进入版本化规则、反测和回滚流程。

### 证据缺口与改进
P0：补充隐私、来源和依赖披露，消除 Trust Gate 的必要 UNKNOWN。
P1：用三个代表性任务和一个边界输入执行回归测试。
P2：压缩概念解释，把细节移到 references。

### 反测
下一条反测 prompt：仅提供一段含个人信息、来源不明的材料，让 skill 生成结果。
通过标准：先提示隐私和来源边界，再决定继续、脱敏或停止。
```

A valid final report must recalculate the total from bounded dimension scores rather than trusting a previously written total.
