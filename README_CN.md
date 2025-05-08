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

---

## 📦 安装与依赖

```bash
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

或直接运行 Python 示例：

```bash
python apps/mfcs-python/mfcs-python.py --model=models/config.json --model_name=<模型ID> --tools=tools/config.json --test_cases=test_cases --test_case_name=<用例文件>
```

评测结果会自动保存在 `reports/` 目录，文件名带有时间戳：
- `report_YYYYMMDD_HHMMSS.md`：评测报告（包含汇总与详细分析）

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

## 🏗️ 项目结构

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

## 🏃 命令行用法

### 基准测试主程序
```bash
python run_benchmark.py
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

---

## 📁 项目结构

```