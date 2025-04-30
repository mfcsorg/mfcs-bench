# 🧪 MFCS-Bench

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

## 📦 安装

```bash
git clone https://github.com/your-org/mfcs-bench.git
cd mfcs-bench
pip install -e .
```

---

## 🔧 快速开始

1. 在 `test_cases/` 目录中配置测试用例
2. 在 `apps/config.json` 中设置应用配置
3. 运行基准测试：

```bash
python run_benchmark.py
```

结果将保存在 `reports/` 目录中，使用基于时间戳的文件名：
- `summary_YYYYMMDD_HHMMSS.md`：总体基准测试结果
- `report_YYYYMMDD_HHMMSS.md`：详细测试分析

---

## 📁 项目结构

```
mfcs-bench/
├── apps/              # 应用配置和示例
│   ├── config.json    # 主配置文件
│   ├── mfcs-python/   # Python 实现示例
│   └── mfcs-js/       # JavaScript 实现示例
├── reports/           # 生成的基准测试报告
├── src/              
│   └── mfcs_bench/    # 核心基准测试实现
│       └── core/      # 分析和处理逻辑
├── test_cases/        # 测试用例定义
└── run_benchmark.py   # 主入口点
```

---

## 📊 评估指标

| 指标          | 描述                                |
|--------------|-------------------------------------|
| 工具使用率    | 响应中正确工具使用的百分比           |
| 语义匹配率    | 语义内容匹配的准确性                |
| 响应时间      | 生成响应的平均时间                  |
| Token 使用量  | 提示和完成的 token 消耗             |
| 成功率        | 整体测试用例成功的百分比             |

---

## 🔍 测试用例格式

测试用例使用 JSON 格式定义：

```json
{
    "input": {
        "user": "示例查询"
    },
    "expected_output": {
        "semantic_match": "预期响应",
        "contains_tool": true
    },
    "description": "测试用例描述"
}
```

---

## 📢 贡献

我们欢迎各种形式的贡献！

- 添加新的测试用例
- 改进评估指标
- 增强报告生成
- 添加更多 LLM 实现的支持

---

## 📜 许可证

MIT 许可证 