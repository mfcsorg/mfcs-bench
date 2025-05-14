# MFCS-Bench

**MFCS-Bench** is a benchmark system for evaluating large language models (LLMs) on function calling tasks, based on the [MFCS (Model Function Calling Standard)](https://github.com/mfcsorg/mfcs) protocol. It standardizes evaluation of how well different models handle structured function calls, helping build a more robust tool-using LLM ecosystem.

[中文文档](README_CN.md)

---

## 🚀 Features

- ✅ **MFCS Protocol Compatible**: Unified interface for evaluating function calls across different LLMs
- 📊 **Comprehensive Metrics**: Tool usage rate, semantic match rate, accuracy, and response time
- 🔄 **Streaming Support**: Real-time response analysis with streaming output
- 📈 **Detailed Reports**: Both summary and detailed markdown reports with test analytics
- 🔁 **Automated Pipeline**: Fully automated benchmark workflow
- ⚡ **Async & Concurrent Evaluation**: Asynchronous, concurrent evaluation of all models and test cases for high efficiency
- 📝 **Async Report Generation**: Benchmark reports are generated asynchronously for better performance
- 📥 **Async Config & Test Case Loading**: Configuration and test cases are loaded with async IO for smoother operation
- 📚 **Custom Embedding Model Support**: Supports custom embedding models for semantic evaluation and similarity threshold configuration

---

## 📦 Installation & Requirements

```bash
git clone https://github.com/mfcsorg/mfcs-bench.git
cd mfcs-bench
pip install -e .
pip install -r requirements.txt
# For Python example:
pip install -r apps/mfcs-python/requirements.txt
```

- Python 3.8+
- Required: `aiofiles`
- For Python example: `mfcs`, `openai`

---

## 🔧 Quick Start

1. Configure your test cases in `test_cases/` directory
2. Set up your application config in `apps/config.json`
3. Set up your model config in `models/config.json`
4. Set up your tool config in `tools/config.json`
5. Run the benchmark:

```bash
python run_benchmark.py
```

Or run the Python example directly:

```bash
python apps/mfcs-python/mfcs-python.py --model=models/config.json --model_name=<model_id> --tools=tools/config.json --test_cases=test_cases --test_case_name=<case.json>
```

Results will be saved to the `reports/` directory with timestamp-based filenames:
- `report_YYYYMMDD_HHMMSS.md`: Benchmark report (includes both summary and detailed analysis)

---

## 📁 Project Structure

```
mfcs-bench/
├── apps/              # Application configs & examples
│   ├── config.json    # Main config
│   ├── mfcs-python/   # Python example
│   └── mfcs-js/       # JS example
├── models/            # Model configs
├── tools/             # Tool configs
├── reports/           # Benchmark reports
├── src/               # Core implementation
│   └── mfcs_bench/
│       └── core/
├── test_cases/        # Test cases
└── run_benchmark.py   # Main entry
```

---

## 📊 Evaluation Metrics

| Metric                | Description                                          |
|----------------------|------------------------------------------------------|
| Tool Usage Rate      | Percentage of correct tool usage in responses        |
| Semantic Match Rate  | Accuracy of semantic content matching                |
| Response Time        | Average time taken to generate responses             |
| Token Usage          | Prompt and completion token consumption              |
| Success Rate         | Overall test case success percentage                 |
| Jaccard Similarity   | Measures the overlap between predicted and expected sets |
| Embedding-based Semantic Match | Measures semantic similarity using embedding models |

> Note: Jaccard Similarity and Embedding-based Semantic Match are alternative metrics; only one is used at a time depending on configuration.

---

## 📢 Test Case Format

Test cases are defined in JSON format:

```json
{
    "input": {
        "user": "example query"
    },
    "expected_output": {
        "semantic_match": "expected response",
        "contains_tool": "get_weather"
    },
    "description": "Test case description"
}
```

---

## 📢 Contribute

We welcome contributions!

- Add new test cases
- Improve evaluation metrics
- Enhance report generation
- Add support for more LLM implementations

---

## 📜 License

MIT License

---

## ⚙️ Configuration

- `apps/config.json`: Application and argument configuration
- `models/config.json`: Model list and API info
- `tools/config.json`: Tool definitions

### Example: apps/config.json
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

### Example: models/config.json
```json
{
  "gpt-4.1-mini": {
    "name": "GPT-4.1 mini",
    "api_base": "https://...",
    "api_key": "sk-..."
  }
}
```

### Example: tools/config.json
```json
[
  {
    "type": "function",
    "function": {
      "name": "web_search_service_xxx",
      "description": "Web search for visually impaired users",
      "parameters": {"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"]}
    }
  }
]
```

---

## 🏃 Command Line Usage

### Benchmark Runner
```bash
python run_benchmark.py
```

**Supported Key Arguments:**

- `--config`: Path to configuration file (default: `apps/config.json`)
- `--reports-dir`: Directory to store reports (default: `reports`)
- `--embedding-model`: Embedding model name or path (optional, default is built-in)
- `--embedding-threshold`: Embedding similarity threshold (optional, default: 0.45)
- `--verbose` or `-v`: Enable verbose logging

**Example:**
```bash
python run_benchmark.py --config=apps/config.json --reports-dir=reports --embedding-model=paraphrase-multilingual-MiniLM-L12-v2 --embedding-threshold=0.45 -v
```

### Python Example
```bash
python apps/mfcs-python/mfcs-python.py --model=models/config.json --model_name=<model_id> --tools=tools/config.json --test_cases=test_cases --test_case_name=<case.json>
```

Arguments:
- `--model`: Path to model config
- `--model_name`: Model ID
- `--tools`: Path to tool config
- `--tools_index`: (optional) Tool index
- `--test_cases`: Path to test cases
- `--test_case_name`: Test case file

---

## 📊 Evaluation & Reports

- Asynchronous, concurrent evaluation of all models and test cases
- Reports include: model, test case, accuracy, response time, tool usage, etc.
- Only one report file is generated: `report_YYYYMMDD_HHMMSS.md` (includes both summary and details)
- Markdown reports saved in `reports/` with timestamp