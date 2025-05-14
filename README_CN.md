# MFCS-Bench

**MFCS-Bench** 是一个基于 [MFCS (模型函数调用标准)](https://github.com/mfcsorg/mfcs) 协议的大语言模型函数调用能力评测系统。它标准化了对不同模型处理结构化函数调用的评估方法，有助于构建更加健壮的工具使用型 LLM 生态系统。

[English](README.md)

---

## 🚀 特性

- ✅ **MFCS 协议兼容**：统一的跨模型函数调用评估接口
- 📊 **全面的评估指标**：工具使用率、语义匹配率、准确率和响应时间
- 🔄 **流式输出支持**：实时的响应分析和流式输出
- 📈 **详细报告**：包含测试分析的汇总和详细 Markdown 报告
- 🔁 **自动化流程**：完全自动化的基准测试工作流
- ⚡ **异步并发评测**：支持所有模型和用例的异步并发评测，极大提升评测效率
- 📝 **异步报告生成**：评测报告异步生成，适合大规模评测
- 📥 **异步配置与用例加载**：配置和测试用例支持异步IO，整体更流畅
- 📚 **自定义Embedding模型支持**：支持自定义embedding模型用于语义评测及相似度阈值配置

---

## 📦 安装与依赖

```bash
git clone https://github.com/mfcsorg/mfcs-bench.git
cd mfcs-bench
pip install -e .
pip install -r requirements.txt
# Python 示例：
pip install -r apps/mfcs-python/requirements.txt
```

- Python 3.8+
- 必需：`aiofiles`
- Python 示例需：`mfcs`、`openai`

---

## 🔧 快速开始

1. 在 `test_cases/` 目录中配置测试用例
2. 在 `apps/config.json` 配置应用
3. 在 `models/config.json` 配置模型
4. 在 `tools/config.json` 配置工具
5. 运行基准测试：

```bash
python run_benchmark.py
```

评测结果会自动保存在 `reports/` 目录，文件名带有时间戳：
- `report_YYYYMMDD_HHMMSS.md`：评测报告（包含汇总与详细分析）

如需更多参数和用法，见下方"命令行用法"章节。

---

## 📁 项目结构

```
mfcs-bench/
├── apps/              # 应用配置与示例
│   ├── config.json    # 主配置
│   ├── mfcs-python/   # Python 示例
│   └── mfcs-js/       # JS 示例
├── models/            # 模型配置
├── tools/             # 工具配置
├── reports/           # 评测报告
├── src/               # 核心实现
│   └── mfcs_bench/
│       └── core/
├── test_cases/        # 测试用例
└── run_benchmark.py   # 主入口
```

---

## 📊 评测指标

| 指标                | 说明                                      |
|---------------------|--------------------------------------------|
| 工具使用率          | 回答中正确调用工具的比例                   |
| 语义匹配率          | 语义内容匹配的准确率                       |
| 响应时间            | 生成回答的平均耗时                         |
| Token 使用量        | prompt 和 completion 的 token 消耗         |
| 成功率              | 测试用例整体通过率                         |
| Jaccard 相似度      | 衡量预测结果与期望结果集合的重叠程度        |
| Embedding 语义匹配  | 使用 embedding 模型计算语义相似度           |

> 注意：Jaccard 相似度和基于 Embedding 的语义匹配为二选一指标，实际评测时仅会根据配置使用其中一种。

---

## 🔍 测试用例格式

测试用例以 JSON 格式定义：

```json
{
    "input": {
        "user": "示例问题"
    },
    "expected_output": {
        "semantic_match": "期望回复",
        "contains_tool": "get_weather"
    },
    "description": "用例描述"
}
```

---

## 📢 贡献

欢迎贡献！

- 新增测试用例
- 改进评测指标
- 优化报告生成
- 支持更多 LLM 实现

---

## 📜 许可证

MIT License

---

## ⚙️ 配置说明

- `apps/config.json`：应用与参数配置
- `models/config.json`：模型列表与API信息
- `tools/config.json`：工具定义

### apps/config.json 示例
```json
{
  "mfcs-python": {
    "command": "python",
    "stream": true,
    "args": [
      "apps/mfcs-python/mfcs-python.py",
      "--model=./models/config.json",
      "--tools=./tools/config.json",
      "--test_cases=./test_cases"
    ]
  }
}
```

### models/config.json 示例
```json
{
  "gpt-4.1-mini": {
    "name": "GPT-4.1 mini",
    "api_base": "https://...",
    "api_key": "sk-..."
  }
}
```

### tools/config.json 示例
```json
[
  {
    "type": "function",
    "function": {
      "name": "web_search_service_xxx",
      "description": "为视障用户提供Web搜索服务",
      "parameters": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]}
    }
  }
]
```

---

## 🏃 命令行用法

### 基准测试主程序
```bash
python run_benchmark.py
```

**支持的关键参数：**

- `--config`：配置文件路径（默认：`apps/config.json`）
- `--reports-dir`：报告输出目录（默认：`reports`）
- `--embedding-model`：embedding模型名称或路径（可选，默认内置）
- `--embedding-threshold`：embedding相似度阈值（可选，默认0.45）
- `--verbose` 或 `-v`：显示详细日志

**示例：**
```bash
python run_benchmark.py --config=apps/config.json --reports-dir=reports --embedding-model=paraphrase-multilingual-MiniLM-L12-v2 --embedding-threshold=0.45 -v
```

### Python 示例
```bash
python apps/mfcs-python/mfcs-python.py --model=models/config.json --model_name=<模型ID> --tools=tools/config.json --test_cases=test_cases --test_case_name=<用例文件>
```

参数说明：
- `--model`：模型配置路径
- `--model_name`：模型ID
- `--tools`：工具配置路径
- `--tools_index`：（可选）工具索引
- `--test_cases`：测试用例目录
- `--test_case_name`：测试用例文件

---

## 📊 评测与报告

- 支持异步并发评测所有模型和用例
- 报告包含：模型、用例、准确率、响应时间、工具使用等详细信息
- Markdown 报告以时间戳命名保存在 `reports/` 目录
- 主要报告文件：
  - `report_YYYYMMDD_HHMMSS.md`：唯一报告文件，包含汇总与详细分析