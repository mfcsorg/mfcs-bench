# 🧪 MFCS-Bench

**MFCS-Bench** is a benchmark system for evaluating large language models (LLMs) on function calling tasks, based on the [MFCS (Model Function Calling Standard)](https://github.com/mfcsorg/mfcs) protocol. It standardizes evaluation of how well different models handle structured function calls, helping build a more robust tool-using LLM ecosystem.

[中文文档](README_CN.md)

---

## 🚀 Features

- ✅ **MFCS Protocol Compatible**: Unified interface for evaluating function calls across different LLMs
- 📊 **Comprehensive Metrics**: Tool usage rate, semantic match rate, accuracy, and response time
- 🔄 **Streaming Support**: Real-time response analysis with streaming output
- 📈 **Detailed Reports**: Both summary and detailed markdown reports with test analytics
- 🔁 **Automated Pipeline**: Fully automated benchmark workflow

---

## 📦 Installation

```bash
git clone https://github.com/your-org/mfcs-bench.git
cd mfcs-bench
pip install -e .
```

---

## 🔧 Quick Start

1. Configure your test cases in `test_cases/` directory
2. Set up your application config in `apps/config.json`
3. Run the benchmark:

```bash
pip install -r apps/mfcs-python/requirements.txt
python run_benchmark.py
```

Results will be saved to the `reports/` directory with timestamp-based filenames:
- `summary_YYYYMMDD_HHMMSS.md`: Overall benchmark results
- `report_YYYYMMDD_HHMMSS.md`: Detailed test analysis

---

## 📁 Project Structure

```
mfcs-bench/
├── apps/              # Application configurations and examples
│   ├── config.json    # Main configuration file
│   ├── mfcs-python/   # Python implementation examples
│   └── mfcs-js/       # JavaScript implementation examples
├── reports/           # Generated benchmark reports
├── src/              
│   └── mfcs_bench/    # Core benchmark implementation
│       └── core/      # Analysis and processing logic
├── test_cases/        # Test case definitions
└── run_benchmark.py   # Main entry point
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

---

## 🔍 Test Case Format

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
