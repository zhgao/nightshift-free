# NightShift Free — 免费版 Merged AI Setup

睡前给一个目标，早上收一份报告卡。把海报里那套 “6 tools, 1 system, 0 manual work”
的付费组合，用**全免费组件**拼出来的开源 v0.1：一条命令跑完 6 步流水线，
生成落地页、社媒草稿（不自动发）、Obsidian 兼容日志和晨间报告卡。

**诚实第一**：没接的指标就是 0 / “not connected”，绝不编造注册数、收入、trending。

## 6 个组件：付费 → 免费对照

| 角色 | 海报里的付费版 | NightShift Free 免费版 |
|---|---|---|
| Brain 大脑 | Opus 5.5 | Gemini 免费层（有 `GEMINI_API_KEY` 时，key 只从环境变量读、绝不存档）；没 key 时用确定性离线模板规划 |
| Researcher 调研 | REA | REA-lite：只读本地目录证据（文件树/类型/README/TODO），不冒充完整逆向工程 |
| Decider 决策 | Jev | 规则版类型化决策（Choice / Score / YesNo + 置信度）+ 硬预算闸：超上限一律拒绝、改选便宜/免费方案（如域名 $49 > 上限 $10 → 选 $3，草案不购买；上限 $0 → GitHub Pages 免费子域名） |
| Connector 编排 | Dots | 本地流水线：`state.json` 断点、失败后可续跑、带时间戳的 `night-shift.log` |
| Scout 外联 | Grok Bot | 只生成 3 条社媒串帖**草稿**；信号只扫你给的本地文本文件。**永不自动发帖** |
| Logger 日志 | Obsidian | Obsidian 兼容 Markdown vault 笔记（wikilinks）+ `cost_ledger.json`，每步每笔成本都记 |

## 3 条命令跑起来

```bash
cp config.example.json config.json   # 可选：改预算上限等
python3 -m nightshift run --goal "为 RecoverLite 做一个落地页" --out runs/demo --target .
python3 -m unittest discover -s tests -v
```

可选环境变量（用 Gemini 免费层时）：`export GEMINI_API_KEY=你的key` ——
只在运行时从环境读，永不写入任何文件、日志或报告。

## 一次运行产出（runs/demo/）

- `plan.json` 规划 · `research.md` 调研证据 · `decisions.json` 类型化决策
- `build/index.html` 落地页（单文件、自带 CSS、离线可开）
- `social_draft.md` 3 条串帖草稿 · `signals.json` 本地信号扫描
- `vault/<日期>-night-shift.md` Obsidian 笔记 · `cost_ledger.json` 成本账（无付费时总额 $0.00）
- `report.html` 晨间报告卡（深色卡片，打开即看：时长/成本/token/步骤；注册=0、收入=$0，均标注 not connected）
- `state.json` 断点 · `night-shift.log` 全程日志

## 诚实局限

- 免费大脑（Gemini Flash 免费层 / 离线模板）明显弱于 Opus 5.5，复杂代码任务别指望同等质量。
- 没有 Grok Bot 那种 24/7 抓 X 的能力；Scout 只有草稿 + 本地信号文件扫描。
- 不自动发帖、不自动购买、不自动买域名：一切花钱/对外动作都是草稿或被预算闸拦下，等本人点头。
- 不保证注册、收入或 trending —— 报告卡里没有接通的数字一律写 0 / not connected。

## 路线图

- v0.2：更多落地页模板、signals 接入本地 RSS/文件监听
- v0.3：可选的本地小模型决策（Kev / NanoJev 类开源替代）
- 之后若验证有人用：再做托管版（$9/mo 构想）——账号、云电脑、报告推送全托管，免费版永远开源

## License

MIT — 见 `LICENSE`。
