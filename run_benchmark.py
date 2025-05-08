"""
MFCS Benchmark Runner
"""
import json
import os
import sys
import argparse
import logging
from datetime import datetime

from mfcs_bench.core.processor import BenchmarkProcessor

def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)

logger = logging.getLogger(__name__)

class BenchmarkRunner:
    """Main benchmark runner class"""
    
    def __init__(self, config_path="apps/config.json", reports_dir="reports"):
        """
        Initialize the benchmark runner
        
        Args:
            config_path: Path to configuration file
            reports_dir: Directory to store reports
        """
        self.config_path = config_path
        self.reports_dir = reports_dir
        self.load_config()
        
        # Ensure reports directory exists
        os.makedirs(self.reports_dir, exist_ok=True)

    def load_config(self) -> None:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info(f"Successfully loaded config file: {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            raise

    def run_benchmark(self) -> None:
        """Run the complete benchmark suite (multi-app, multi-model, multi-test_case)"""
        results = {}
        for app_name, app_config in self.config.items():
            results[app_name] = {}
            # 1. Load all models
            model_cfg_path = None
            for arg in app_config["args"]:
                if arg.startswith("--model=") or arg.startswith("--models="):
                    model_cfg_path = arg.split("=", 1)[1]
            if not model_cfg_path:
                logger.error(f"No model config path found for app {app_name}")
                continue
            with open(model_cfg_path, 'r', encoding='utf-8') as f:
                models = json.load(f)
            # 2. Load all test cases
            test_cases_dir = None
            for arg in app_config["args"]:
                if arg.startswith("--test_cases="):
                    test_cases_dir = arg.split("=", 1)[1]
            if not test_cases_dir:
                logger.error(f"No test_cases dir found for app {app_name}")
                continue
            test_case_files = [f for f in os.listdir(test_cases_dir) if f.endswith('.json')]
            # 3. Iterate over models and test cases
            for model_name in models.keys():
                results[app_name][model_name] = {}
                for test_case_file in test_case_files:
                    # Dynamically assemble command
                    command = [app_config["command"]] + [a for a in app_config["args"]]
                    # Add model name parameter
                    if any(a.startswith("--model=") for a in command):
                        command.append(f"--model_name={model_name}")
                    elif any(a.startswith("--models=") for a in command):
                        command.append(f"--model_name={model_name}")
                    # Add test case name parameter
                    command.append(f"--test_case_name={test_case_file}")
                    # Construct new app_config including test_case_name parameter
                    app_config_with_case = dict(app_config)
                    app_config_with_case["args"] = list(app_config["args"]) + [f"--test_case_name={test_case_file}"]
                    logger.info(f"Running: {app_name} | {model_name} | {test_case_file}")
                    processor = BenchmarkProcessor()
                    result = processor.process_app(command, app_config_with_case, app_name)
                    # Record model name and test case name
                    result["model_name"] = model_name
                    result["test_case_file"] = test_case_file
                    results[app_name][model_name][test_case_file] = result
        self.generate_report(results)

    def generate_report(self, results):
        """Generate benchmark reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate complete report
        self._generate_complete_report(results, timestamp)

    def _generate_complete_report(self, results, timestamp):
        """Generate complete report with summary and details"""
        report_path = os.path.join(self.reports_dir, f"report_{timestamp}.md")
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                self._write_summary_section(f, results)
                self._write_detailed_sections(f, results)
            
            logger.info(f"Report generated: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise

    def _write_summary_section(self, f, results):
        """Write the summary section of the report"""
        f.write("# MFCS Evaluation Report\n\n")
        f.write("## Summary\n\n")
        f.write("| App Name | Model | Test Case | Accuracy | Response Time | Pass Rate | Tool Usage | Result |\n")
        f.write("|----------|--------|-----------|----------|---------------|-----------|------------|--------|\n")
        for app_name, models in results.items():
            for model_name, test_cases in models.items():
                for test_case_file, result in test_cases.items():
                    analysis = result["analysis"]
                    accuracy = f"{analysis.get('accuracy', 0.0):.2f}%"
                    avg_response_time = f"{result['execution_time']:.2f}s"
                    test_case_success = f"{(100.0 if result.get('success', False) else 0.0):.2f}%"
                    tool_usage = analysis.get("tool_usage", "none")
                    tool_usage_display = "none" if tool_usage == "none" else f"{100.0 if tool_usage != 'no' else 0.0:.2f}%"
                    status = "✅ Pass" if result.get('success', False) else "❌ Fail"
                    f.write(f"| {app_name} | {model_name} | {test_case_file} | {accuracy} | {avg_response_time} | {test_case_success} | {tool_usage_display} | {status} |\n")
        f.write("\n---\n\n")

    def _write_detailed_sections(self, f, results):
        """Write the detailed sections for each app"""
        for app_name, models in results.items():
            f.write(f"# {app_name}\n\n")
            for model_name, test_cases in models.items():
                f.write(f"## {model_name}\n\n")
                f.write(f"### Test Overview\n\n")
                f.write(f"- **Model**: {model_name}\n")
                f.write(f"- **Evaluation Time**: {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write(f"- **Test Cases**: {len(test_cases)}\n\n")
                f.write(f"### Test Results\n\n")
                f.write("| Test Case | Tool Usage | Required Content | Semantic Match | Accuracy |\n")
                f.write("|-----------|------------|------------------|----------------|----------|\n")
                for test_case_file, result in test_cases.items():
                    analysis = result["analysis"]
                    tool_usage = analysis.get("tool_usage", "none")
                    required_content = analysis.get("required_content", "none")
                    semantic_match = analysis.get("semantic_match", "none")
                    accuracy = f"{analysis.get('accuracy', 0.0):.2f}%"
                    f.write(f"| {test_case_file} | {tool_usage} | {required_content} | {semantic_match} | {accuracy} |\n")
                f.write("\n")
                for test_case_file, result in test_cases.items():
                    test_case = result.get("test_case", {})
                    analysis = result["analysis"]
                    f.write(f"#### {test_case_file}\n\n")
                    f.write(f"**Input**: `{json.dumps(test_case.get('input', {}), ensure_ascii=False)}`\n\n")
                    f.write(f"**Expected Output**: \n```json\n{json.dumps(test_case.get('expected_output', {}), ensure_ascii=False, indent=2)}\n```\n\n")
                    f.write("**Actual Output**:\n```\n")
                    if result.get("stdout"):
                        f.write(result["stdout"])
                    f.write("```\n\n")
                    f.write(f"- **Accuracy**: {analysis.get('accuracy', 0.0):.2f}%\n")
                    f.write(f"- **Tool Usage**: {analysis.get('tool_usage', 'none')}\n")
                    f.write(f"- **Required Content Match**: {analysis.get('required_content', 'none')}\n")
                    f.write(f"- **Semantic Match**: {analysis.get('semantic_match', 'none')}\n\n")
                f.write("---\n\n")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="MFCS Benchmark Runner - Test and evaluate MFCS implementations"
    )
    
    parser.add_argument(
        "--config",
        default="apps/config.json",
        help="Path to configuration file (default: apps/config.json)"
    )
    
    parser.add_argument(
        "--reports-dir",
        default="reports",
        help="Directory to store reports (default: reports)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

def main() -> int:
    """Main entry point"""
    args = parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    try:
        runner = BenchmarkRunner(
            config_path=args.config,
            reports_dir=args.reports_dir
        )
        runner.run_benchmark()
        return 0
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
