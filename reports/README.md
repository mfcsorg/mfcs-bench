# MFCS Benchmark Reports

This directory contains benchmark reports and analysis results for the MFCS (Model Function Calling System) benchmark suite.

## Contents

Each benchmark run generates a comprehensive report file (`report_YYYYMMDD_HHMMSS.md`) that includes:

### Summary Section
Provides overall benchmark results including:
- Model Performance Metrics
  - Accuracy and precision
  - Response time analysis
  - Success rate by test category
- Resource Usage
  - Tool usage statistics and patterns
  - Token consumption metrics
  - Memory utilization
- Test Status Overview
  - Pass/fail statistics
  - Error categorization
  - Performance bottlenecks

### Detailed Section
In-depth analysis for each test case including:
- Test Environment
  - System configuration
  - Model parameters
  - Runtime settings
- Test Results Analysis
  - Input/output comparison
  - Tool usage breakdown
  - Response validation
- Performance Metrics
  - Semantic matching results
  - Token usage details
  - Execution time analysis
- Error Analysis
  - Failure patterns
  - Edge cases
  - Improvement suggestions

## Organization

Reports are organized using the following structure:
- Timestamp-based directories (YYYYMMDD_HHMMSS format)
  - Complete report file
  - Raw data and metrics
  - Visualization outputs (if applicable)

Reports are automatically generated when running benchmarks using the `run_benchmark.py` script. Each benchmark run creates a new timestamped directory to maintain historical data.

## Usage

To generate new reports:
1. Run `run_benchmark.py` with desired configuration
2. A new report will be automatically generated with timestamp-based filename
3. The report contains both summary and detailed sections for comprehensive analysis

For historical analysis, reports can be compared across different timestamps to track performance trends and improvements. 