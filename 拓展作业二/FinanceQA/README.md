# 企业财务问答 Agent 作业数据

本作业要求自行设计一个可复用的大模型 Agent，根据公司标识和问题，查询财务数据库、检索年报并进行必要计算，给出有依据的回答。本包提供数据和独立评测材料，Agent 代码与运行方式由同学自行实现。

## 提供的数据

- **SQLite 财务数据库**：六家公司的结构化财务指标，可用于查询、跨期比较和指标计算。
- **9 份年报正文**：六家公司各自最新一期年报，以及三份历史对照；HTML 中保留业务介绍、风险披露、财务报表与附注。
- **56 道英文问题及参考答案**：train 为四家公司 37 题，test 为两家公司 19 题。train 用于开发和优化 Agent，不要求训练模型参数。
- **独立评测材料**：评测程序、检查器提示词及 test 参考答案，作答完成后单独使用。

数据库和年报各有用途：财务数值适合通过 SQL 查询和计算，产品、战略、风险等信息通常需要检索年报。无需把全部年报一次放入模型上下文，可自行建立目录或索引，按公司、报告期和问题检索相关段落或表格。

## 阅读顺序

1. [TASK.md](TASK.md)：任务要求、可自由设计的部分及文件使用边界。
2. [数据使用与作业完成流程.md](数据使用与作业完成流程.md)：理解数据、train 优化、test 作答和独立评测的整体流程。
3. [评测说明.md](evaluation_only/评测说明.md)：评测脚本的具体命令和参数。

## 文件用途

| 路径 | 用途 |
|---|---|
| `agent_workspace/data/finance.db` | 财务数据库，Agent 可读取 |
| `agent_workspace/data/schema.md`、`business_rules.md` | 英文表结构说明和通用数据口径，Agent 可读取 |
| `agent_workspace/data/companies.json` | 公司名称、CIK、train/test 划分及题数 |
| `agent_workspace/data/filings/README.md` | 英文年报目录，按公司和报告期列出本地文件 |
| `agent_workspace/data/filings/<CIK>/*.htm` | Agent 可读取的年报正文 |
| `agent_workspace/train/` | 开发问题与参考答案；可用于优化方法 |
| `agent_workspace/test/questions.json` | 固定方法后统一作答的问题 |
| `agent_workspace/prompts/agent_system.txt` | 可修改的基础 system prompt |
| `agent_workspace/contracts/` | 固定的任务输入与预测输出格式 |
| `evaluation_only/` | 独立评分材料，作答 Agent 不得读取 |

同学可在 `agent_workspace/` 中自行建立代码、索引、Skill、memory 和输出目录。保留提供的数据原文件，派生文件另存。参考答案和独立评测材料虽然公开，**test 答案及评分反馈不得用于设计方法或生成回答**。
