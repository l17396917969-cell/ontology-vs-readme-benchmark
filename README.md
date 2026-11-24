# 本体真的不如 README 吗？

用同一套合成业务资料，比较全文阅读、按需找 README、按对象关系找证据和调用受控动作。题库包含问数、跨域回款、工单写入，以及没有预先写明的供应链、复产和审批隐患。

The benchmark compares full Markdown, retrieval over Markdown, and object-path retrieval on matched synthetic business records. It includes repeatable structured reads and writes, plus previously unstated operational risks. The archived API responses support offline scoring.

## 三组实验

| 实验 | 实际测了什么 | 入口 |
| --- | --- | --- |
| 目录检索 | 40 题，目录规模与底表行数分开改变。全文、关键词、关系、按域查找和直接给证据。 | [方法和结果](metadata-retrieval/README.md) · [题库](metadata-retrieval/questions.json) · [复核题](metadata-retrieval/follow-up-questions.json) |
| 读写动作 | 20 题，分别判意图、最终回执和写入状态。按域查文档和图路径共享同一组严格函数。 | [方法和结果](object-actions/README.md) · [题库](object-actions/questions.json) · [对象关系与动作](object-actions/object-schema.json) |
| 新风险发现 | 三类隐患各有三态，乘两档目录共 18 个场景；测试 35 与 755 张资料。 | [方法和结果](risk-discovery/README.md) · [源记录](risk-discovery/core-cards.json) · [问题与逐题结果](risk-discovery/results.json) |

读写动作的全文 README 组得到 40/40 正确回执。两个严格函数组同为 40/40，对象路径少用约 60% 输入 token。大目录风险实验，全文组结论与证据齐全为 6/18，对象路径为 15/18。解析 Markdown 里的显式链接再做同样的遍历，两个路径会取得逐字一致的资料。 [读写原始评分](object-actions/typed-results.json) · [风险原始评分](risk-discovery/results.json)

## 模型和数据

模型 API 名称为 `deepseek-flash`，调用时响应也返回该别名。统一禁用 thinking，temperature 0，每道题由新的请求执行。各组的输出预算和重复次数在协议及代码中。严格接口复验使用 DeepSeek Beta 的工具调用。模型服务别名会随提供方升级，重新调用的回包和时间可能与归档不同。归档的 596 条响应都使用合成资料，服务端请求标识已散列，模型答案、token、耗时及判分可复核。 [模型说明](https://api-docs.deepseek.com/quick_start/pricing/) · [一手调研](research.md)

## 离线核对

需 Python 3.11 或更高版本。如下命令不使用 API 凭证。验证脚本将原始回包复制到临时目录，重建 SQLite 快照、重新执行与评分，再对照归档的逐题结果。

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 verify.py
```

## 重新跑模型

先在环境中设置自己的 `DEEPSEEK_API_KEY`，选择有预算的实验。让每组使用单独的输出目录，以便和已发表结果比较。

```sh
BENCH_ARTIFACT_DIR=runs/retrieval python3 metadata-retrieval/run.py run
BENCH_ARTIFACT_DIR=runs/retrieval python3 metadata-retrieval/follow_up.py --run
BENCH_ARTIFACT_DIR=runs/actions python3 object-actions/compare.py run
BENCH_ARTIFACT_DIR=runs/actions python3 object-actions/typed_compare.py --run
BENCH_ARTIFACT_DIR=runs/risk python3 risk-discovery/run.py run
```

## 欢迎挑战

欢迎提交更强的 README 检索、另一种关系建模、不同模型复跑，或新的隐藏风险题。PR 里附策略、配置、取到的证据与实际回执。可先用 Issues 讨论不同判分口径。 [挑战与提交口径](CHALLENGE.md) · [GitHub Issues](https://github.com/l17396917969-cell/ontology-vs-readme-benchmark/issues)
