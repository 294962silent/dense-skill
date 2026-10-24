# dense — 一个省 token 但不牺牲准确性的输出技能

一个 120 token 的 Agent Skill：让模型少写废话，同时把任务做完。

在 16 道题 × 10 次重复的对照实验里（`deepseek-v4.1-flash`，480 次调用）：

| 臂 | 通过率 | 计费输出 | 用户可见文本 | 单次总成本 |
|---|---:|---:|---:|---:|
| `Answer concisely.` 基线 | 93.8% | 349 | 97 | 409 |
| **dense（本仓库）** | **97.5%** | **201（−42%）** | **39（−60%）** | **364（−11%）** |
| caveman（1112 token） | 93.8% | 340（+1.3%，区间跨 0） | 108 | 1495（+279%） |

通过率差值与基线在噪声范围内（两轮独立运行分别为 −3.1pp 和 +3.8pp），所以准确说法是**精度不可区分、输出显著更少**，而不是「更准」。

## 技能正文

只有五条：

1. 答案在第一行。
2. 用户没要的不加：不加章节、例子、下一步。
3. 代码、命令、路径、数字、错误逐字复制。
4. 安全警告、不可逆操作、必需步骤、被要求的字段永不删。
5. 选择题给选择、一个决定性理由、以及被否掉的选项。

外加删除客套、结尾、自述、对冲、模型腔。完整文件见 [skill/dense/SKILL.md](skill/dense/SKILL.md)。

## 安装

```bash
mkdir -p ~/.agents/skills/dense
curl -fsSL https://raw.githubusercontent.com/294962silent/dense-skill/main/skill/dense/SKILL.md -o ~/.agents/skills/dense/SKILL.md
```

任何读 `SKILL.md` 的宿主都能用（Claude Code、Codex、Cursor、DSH 等）。说「简洁点 / 少点 token / 别啰嗦」触发。

## 为什么只有 120 token

社区里最有名的几个压缩技能是 1000–1700 token，而证据指向相反：注入的每一 token 每次调用都要付钱。`caveman-micro` 用 1/6 的体积打赢原版；本文的实验里，同一套规则写成 123 token 时计费输出 −42%，写成 342 token 时**反而 +28%**——长规则让模型多想了 76 个推理 token。

## 实验结果

完整报告：[REPORT.md](REPORT.md)。调研笔记：[research/findings.md](research/findings.md)。实验协议：[bench/DESIGN.md](bench/DESIGN.md)。

三个发现：

- **压缩有一半省在用户看不见的地方**：349 计费输出里 213 是隐藏推理，可见文本只有 97。只报「−42%」会让人误以为正文短了一半。
- **短技能赢**：dense(123) > dense_v4(221) > dense_v1(342)，规则越少越能执行。
- **最流行的技能在这个基准上不省**：caveman 计费输出与基线无显著差异，但每次多付约 1100 输入 token。

## 复现

```bash
cd bench
python run.py --reps 10 --arms terse,dense --out results/repro.jsonl
python analyze.py results/repro.jsonl
```

`run.py` 读取 `$OPENAI_BASE_URL` 与 `~/.dsh/.credentials.yaml` 里的 key，默认模型 `deepseek-v4.1-flash`。任务与评分正则在 `bench/tasks.json`，原始响应在 `bench/results/`。

## 局限

单模型、单温度、单轮问答；正则评分只验证「必需事实在不在」，验证不了理由对不对；16 题里只有 4 道留出题。跨模型不可外推。

## License

MIT
