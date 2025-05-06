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

    def run_app(self, app_name: str) -> dict:
        """Run a specific test application"""
        if app_name not in self.config:
            raise ValueError(f"Application configuration not found: {app_name}")

        app_config = self.config[app_name]
        command = [app_config["command"]] + app_config["args"]
        
        logger.info(f"Starting application: {app_name}")
        logger.info(f"Executing command: {' '.join(command)}")
        
        processor = BenchmarkProcessor()
        return processor.process_app(command, app_config, app_name)

    def run_benchmark(self) -> None:
        """Run the complete benchmark suite"""
        results = []
        for app_name in self.config:
            try:
                result = self.run_app(app_name)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to run application {app_name}: {e}")
                results.append({
                    "app_name": app_name,
                    "success": False,
                    "error": str(e),
                    "execution_time": 0,
                    "analysis": {
                        "tool_usage": "none",
                        "required_content": False,
                        "semantic_match": "no",
                        "accuracy": 0.0,
                        "response_time": 0.0,
                        "token_usage": {"prompt": 0, "completion": 0}
                    }
                })
        
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
        f.write("| App Name | Model | Accuracy | Response Time | Pass Rate | Tool Usage | Result |\n")
        f.write("|----------|--------|----------|---------------|-----------|------------|--------|\n")
        
        for result in results:
            app_name = result["app_name"]
            analysis = result["analysis"]
            test_case = result.get("test_case", {})
            
            model_name = analysis.get("model", test_case.get("model", "unspecified"))
            accuracy = f"{analysis.get('accuracy', 0.0):.2f}%"
            avg_response_time = f"{result['execution_time']:.2f}s"
            test_case_success = f"{(100.0 if result.get('success', False) else 0.0):.2f}%"
            tool_usage = analysis.get("tool_usage", "none")
            tool_usage_display = "none" if tool_usage == "none" else f"{100.0 if tool_usage != 'no' else 0.0:.2f}%"
            status = "✅ Pass" if result.get('success', False) else "❌ Fail"
            
            f.write(f"| {app_name} | {model_name} | {accuracy} | {avg_response_time} | "
                   f"{test_case_success} | {tool_usage_display} | {status} |\n")
        
        f.write("\n---\n\n")  # Add a separator between summary and detailed reports

    def _write_detailed_sections(self, f, results):
        """Write the detailed sections for each app"""
        for result in results:
            self._write_app_details(f, result)
            f.write("---\n\n")  # Add a separator between app reports

    def _write_app_details(self, f, result):
        """Write detailed section for a single app"""
        app_name = result["app_name"]
        analysis = result["analysis"]
        test_case = result.get("test_case", {})
        
        f.write(f"# {app_name} Evaluation Details\n\n")
        
        f.write("## Test Overview\n\n")
        f.write(f"This evaluation tests the capabilities of {app_name}.\n\n")
        
        f.write("## Test Environment\n\n")
        model_name = analysis.get("model", test_case.get("model", "unspecified"))
        
        # Get test case name from application response
        test_case_name = "unknown"
        if result.get("responses"):
            first_response = result["responses"][0]
            if first_response and "test_case" in first_response:
                test_case_name = first_response["test_case"]
        
        f.write(f"- **Model**: {model_name}\n")
        f.write(f"- **Evaluation Time**: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"- **Test Cases**: 1\n\n")
        
        self._write_test_results(f, result, test_case, test_case_name)

    def _write_test_results(self, f, result, test_case, test_case_name):
        """Write test results section"""
        analysis = result["analysis"]
        
        f.write("## Test Results\n\n")
        
        # Evaluation Details Table
        f.write("### Evaluation Details\n\n")
        f.write("| Test Case | Tool Usage | Required Content | Semantic Match | Accuracy |\n")
        f.write("|-----------|------------|------------------|----------------|----------|\n")
        
        tool_usage = analysis.get("tool_usage", "none")
        required_content = analysis.get("required_content", "none")
        semantic_match = analysis.get("semantic_match", "none")
        accuracy = f"{analysis.get('accuracy', 0.0):.2f}%"
        
        if "contains_tool" not in test_case.get("expected_output", {}):
            tool_usage = "none"
        
        f.write(f"| {test_case_name} | {tool_usage} | {required_content} | "
               f"{semantic_match} | {accuracy} |\n\n")
        
        # Overall Metrics
        f.write("### Overall Metrics\n\n")
        f.write(f"- **Accuracy**: {analysis.get('accuracy', 0.0):.2f}%\n")
        tool_usage_display = "none" if tool_usage == "none" else f"{100.0 if tool_usage != 'no' else 0.0:.2f}%"
        f.write(f"- **Tool Usage**: {tool_usage_display}\n")
        required_content_display = "none" if required_content == "none" else f"{100.0 if required_content == 'yes' else 0.0:.2f}%"
        f.write(f"- **Required Content Match Rate**: {required_content_display}\n")
        f.write(f"- **Semantic Match Rate**: {100.0 if semantic_match == 'yes' else 0.0:.2f}%\n")
        f.write(f"- **Average Response Time**: {result['execution_time']:.2f} seconds\n")
        f.write(f"- **Token Usage**: {json.dumps(analysis.get('token_usage', {'prompt': 0, 'completion': 0}))}\n")
        f.write(f"- **Average Tokens per Response**: {(analysis.get('token_usage', {}).get('completion', 0) / max(1, len(result.get('responses', [])))):.2f}\n\n")
        
        # Detailed Response Analysis
        f.write("### Detailed Response Analysis\n\n")
        f.write(f"#### {test_case.get('description', 'Test Case')}\n\n")
        f.write(f"**Input**: `{json.dumps(test_case.get('input', {}), ensure_ascii=False)}`\n\n")
        f.write(f"**Expected Output**: \n```json\n{json.dumps(test_case.get('expected_output', {}), ensure_ascii=False, indent=2)}\n```\n\n")
        f.write("**Actual Output**:\n```\n")
        if result.get("stdout"):
            f.write(result["stdout"])
        f.write("```\n\n")
        
        f.write(f"**Accuracy**: {analysis.get('accuracy', 0.0):.2f}%\n")
        f.write(f"**Tool Usage**: {analysis.get('tool_usage', 'none')}\n")
        f.write(f"**Required Content Match**: {analysis.get('required_content', 'none')}\n")
        f.write(f"**Semantic Match**: {analysis.get('semantic_match', 'none')}\n\n")

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
