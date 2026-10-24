# 社区 token 压缩 skill 调研

调研对象：GitHub 上 6 个主流「输出压缩」skill，全部 clone 到 `research/repos/` 并读源码与自带评测。

| skill | 注入体积（本文实测） | 核心机制 | 自带证据 |
|---|---:|---|---|
| [caveman](https://github.com/JuliusBrussee/caveman) | 1107 tok | 9 条规则 + 自动降级 + 发送前自检；强调「是口吻不是烂语法」 | 三臂评测，只有长度臂；fidelity 快照未提交 |
| [introvert](https://github.com/DeepakGanapathi97/introvert) | 1681 tok | 完整句、两级长度规格、模型腔黑名单、verbatim 保护 | 声称最多 −75%，无公开对照数据 |
| [scrooge-mode](https://github.com/Kir93/scrooge-mode) | 1723 tok | 五语种 register，BLUF，`lean` 代码开关 | 有配对 benchmark，`lean` 实测 +17.6%/−18.1% |
| [laconic](https://github.com/GabrielBarberini/laconic) | 447 tok | 哲学式：省略可推断的一切 | 无量化 |
| [caveman-distillate](https://github.com/dlepold/caveman-distillate) | 465 tok | caveman 的极简版 + 前后对照例 | 声称 ~65% |
| [caveman-micro](https://github.com/kuba-guzik/caveman-micro) | **85 tok** | 6 行「许可」而非教程 | 2 任务 × 3 次，Sonnet −14% / Opus −21%，质量 100% |

## 三个反直觉的发现

**1. 最有名的 skill 注入最大，而证据指向「越短越好」。**
caveman 全文约 1100 token，introvert / scrooge 约 1700。caveman-micro 只留 6 行，却在 Sonnet 与 Opus 上同时打赢了 552 词的原版。它的解释是对的：模型本来就会简洁，它需要的是**许可**，不是教程。注入的每一 token 每次调用都要付钱。

**2. 所有评测都只数输出 token，没人算总成本。**
caveman 自己的 `evals/README.md` 明确写着：「Skills add input tokens on every call, so output savings are not the full economic picture」。但它和几乎所有同类仍然只报输出降幅。粗算：1700 token 的技能每次调用要先多付 1700 输入，若输出只省 60 token，净亏 1600+。**只有长会话 + 提示缓存才可能回本。**

**3. 「质量 100%」这个指标太松，测不出压过头。**
caveman-micro 用结构化 JSON 输出 + 固定字段校验，2 个任务、3 次重复，全部 100%。这种检查只能发现「字段丢了」，发现不了「理由没了」「否定词反了」「步骤顺序乱了」。caveman 的 fidelity 用例设计得更好（must_include / must_not_include 正则 + 正反例自检），但**快照至今未提交**，也就是没有公开发布过的 fidelity 数字。

## 各家的独门贡献（值得吸收）

- **caveman**：`Payload verbatim`（代码/命令/路径/错误原样）、`auto-clarity` 降级清单（安全警告、不可逆操作、顺序会乱、用户困惑、反问用户）、`pre-send check`、以及「绝不表演 caveman」这条元规则。
- **introvert**：**长度是规格而不是副作用**（standard/max 两级，且明说两级输出长度必须不同）；完整句底线（碎片是缺陷不是压缩）；**模型腔黑名单**（delve/crucial/robust… 一整个词表）；把「否定词、条件、纠错动作」列为永不可删。
- **scrooge**：BLUF（结论先行）；`lean` 只压代码不压语义；多语种 register 承认「压缩的是风格不是语言」；决策题只要答案 + 一个决定性理由。
- **caveman-micro**：极短注入 + 「模型腔/客套/缩减同义词」三件套；以及那句最有价值的判断——**最大的节省来自基础 prompt，不来自输出压缩**。
- **laconic / distillate**：用例子而不是规则定义期望长度（distillate 的 69→19 token 对照非常直观）。

## 共同缺陷

1. **不区分任务类型**：同一个规则去压「解释为什么」和压「给我个命令」，前者被压废、后者被压不够。
2. **只删不增**：没有一条规则说「用户没要的东西不要加」。实测里模型会主动补 SQL、补边界条件、补下一步，这是最大的隐形成本。
3. **注入成本无人核算**，于是大家都在比谁的规则更全，而不是谁的净收益更高。
4. **没有一条规则把「精准」定义清楚**：多数只写「技术细节保留」，没有可检验的清单。

## 由此得到的设计约束

1. **注入必须短**：目标 ≤350 token（caveman 的 1/3，introvert 的 1/5），细节放 `reference.md` 按需读。
2. **按任务类型给预算**，不搞一把尺子。
3. **加一条「停在答案处」**：闭式问题只要答案；未要求的代码、例子、下一步都算 padding。
4. **精准要可检验**：必须项清单 + 否定/条件/顺序不可删 + payload 逐字节。
5. **评测要报总成本**（输入 + 输出），并且用确定性正则做 fidelity，而不是只数 token 或只看「字段在不在」。

这 5 条就是 `skill/dense` 的由来，也是 `bench/` 要验证的东西。
