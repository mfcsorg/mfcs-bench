"""
MFCS Benchmark Runner
"""
import json
import os
import sys
import argparse
import logging
from datetime import datetime
import asyncio
import aiofiles
from sentence_transformers import SentenceTransformer

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
    
    def __init__(self, config_path="apps/config.json", reports_dir="reports", embedding_model_name_or_path=None, embedding_threshold=None):
        """
        Initialize the benchmark runner
        
        Args:
            config_path: Path to configuration file
            reports_dir: Directory to store reports
            embedding_model_name_or_path: Embedding model name or path
            embedding_threshold: Embedding similarity threshold
        """
        self.config_path = config_path
        self.reports_dir = reports_dir
        self.embedding_model_name_or_path = embedding_model_name_or_path
        self.embedding_threshold = embedding_threshold
        # 只加载一次 embedding_model
        model_name = (
            embedding_model_name_or_path or
            os.environ.get('EMBEDDING_MODEL_NAME_OR_PATH') or
            BenchmarkProcessor.DEFAULT_EMBEDDING_MODEL
        )
        self.embedding_model = SentenceTransformer(model_name)
        self.load_config()
        
        # Ensure reports directory exists
        os.makedirs(self.reports_dir, exist_ok=True)
        # Load all model display names for all apps
        self.model_display_names = {}  # {model_id: "model_id (中文名)"}
        self._load_all_model_display_names()

    def _load_all_model_display_names(self):
        """Load all model display names from all model config paths in apps config."""
        model_paths = set()
        for app_config in self.config.values():
            for arg in app_config["args"]:
                if arg.startswith("--model=") or arg.startswith("--models="):
                    model_paths.add(arg.split("=", 1)[1])
        for path in model_paths:
            if not os.path.exists(path):
                continue
            with open(path, 'r', encoding='utf-8') as f:
                models = json.load(f)
                for model_id, model_info in models.items():
                    cn_name = model_info.get("name", "")
                    if cn_name:
                        self.model_display_names[model_id] = f"{model_id} ({cn_name})"
                    else:
                        self.model_display_names[model_id] = model_id

    def get_model_display_name(self, model_id):
        return self.model_display_names.get(model_id, model_id)

    def load_config(self) -> None:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info(f"Successfully loaded config file: {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            raise

    async def async_load_config(self) -> None:
        try:
            async with aiofiles.open(self.config_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                self.config = json.loads(content)
            logger.info(f"Successfully loaded config file: {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            raise

    async def async_run_benchmark(self):
        """Asynchronously run all benchmark tasks concurrently"""
        results = {}
        tasks = []
        task_map = {}  # task -> (app_name, model_name, test_case_file)
        await self.async_load_config()
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
            async with aiofiles.open(model_cfg_path, 'r', encoding='utf-8') as f:
                models = json.loads(await f.read())
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
                    command = [app_config["command"]] + [a for a in app_config["args"]]
                    if any(a.startswith("--model=") for a in command):
                        command.append(f"--model_name={model_name}")
                    elif any(a.startswith("--models=") for a in command):
                        command.append(f"--model_name={model_name}")
                    command.append(f"--test_case_name={test_case_file}")
                    app_config_with_case = dict(app_config)
                    app_config_with_case["args"] = list(app_config["args"]) + [f"--test_case_name={test_case_file}"]
                    logger.info(f"Running: {app_name} | {model_name} | {test_case_file}")
                    processor = BenchmarkProcessor(embedding_model=self.embedding_model, embedding_threshold=self.embedding_threshold)
                    coro = processor.async_process_app(command, app_config_with_case, app_name)
                    task = asyncio.create_task(coro)
                    tasks.append(task)
                    task_map[task] = (app_name, model_name, test_case_file)
        # Wait for all tasks concurrently
        finished = await asyncio.gather(*tasks)
        # Assemble results
        for task, result in zip(tasks, finished):
            app_name, model_name, test_case_file = task_map[task]
            result["model_name"] = model_name
            result["test_case_file"] = test_case_file
            results[app_name][model_name][test_case_file] = result
        await self.async_generate_report(results)

    async def async_generate_report(self, results):
        """Generate benchmark reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        await self._async_generate_complete_report(results, timestamp)

    async def _async_generate_complete_report(self, results, timestamp):
        """Generate complete report with summary and details"""
        report_path = os.path.join(self.reports_dir, f"report_{timestamp}.md")
        
        try:
            async with aiofiles.open(report_path, 'w', encoding='utf-8') as f:
                await self._async_write_summary_section(f, results)
                await self._async_write_detailed_sections(f, results)
            
            logger.info(f"Report generated: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise

    async def _async_write_summary_section(self, f, results):
        """Write the summary section of the report"""
        await f.write("# MFCS Evaluation Report\n\n")
        await f.write("## Summary\n\n")
        await f.write("| App Name | Model | Test Case | Accuracy | Response Time | Pass Rate | Tool Usage | Result |\n")
        await f.write("|----------|--------|-----------|----------|---------------|-----------|------------|--------|\n")
        for app_name, models in results.items():
            for model_name, test_cases in models.items():
                model_display = self.get_model_display_name(model_name)
                for test_case_file, result in test_cases.items():
                    analysis = result["analysis"]
                    accuracy = f"{analysis.get('accuracy', 0.0):.2f}%"
                    avg_response_time = f"{result['execution_time']:.2f}s"
                    test_case_success = f"{(100.0 if result.get('success', False) else 0.0):.2f}%"
                    tool_usage = analysis.get("tool_usage", "none")
                    tool_usage_display = "none" if tool_usage == "none" else f"{100.0 if tool_usage != 'no' else 0.0:.2f}%"
                    status = "✅ Pass" if result.get('success', False) else "❌ Fail"
                    await f.write(f"| {app_name} | {model_display} | {test_case_file} | {accuracy} | {avg_response_time} | {test_case_success} | {tool_usage_display} | {status} |\n")
        await f.write("\n---\n\n")

    async def _async_write_detailed_sections(self, f, results):
        """Write the detailed sections for each app"""
        for app_name, models in results.items():
            await f.write(f"# {app_name}\n\n")
            for model_name, test_cases in models.items():
                model_display = self.get_model_display_name(model_name)
                await f.write(f"## {model_display}\n\n")
                await f.write(f"### Test Overview\n\n")
                await f.write(f"- **Model**: {model_display}\n")
                await f.write(f"- **Evaluation Time**: {datetime.now().strftime('%Y-%m-%d')}\n")
                await f.write(f"- **Test Cases**: {len(test_cases)}\n\n")
                await f.write(f"### Test Results\n\n")
                await f.write("| Test Case | Tool Usage | Required Content | Semantic Match | Accuracy |\n")
                await f.write("|-----------|------------|------------------|----------------|----------|\n")
                for test_case_file, result in test_cases.items():
                    analysis = result["analysis"]
                    tool_usage = analysis.get("tool_usage", "none")
                    required_content = analysis.get("required_content", "none")
                    semantic_match = analysis.get("semantic_match", "none")
                    accuracy = f"{analysis.get('accuracy', 0.0):.2f}%"
                    await f.write(f"| {test_case_file} | {tool_usage} | {required_content} | {semantic_match} | {accuracy} |\n")
                await f.write("\n")
                for test_case_file, result in test_cases.items():
                    test_case = result.get("test_case", {})
                    analysis = result["analysis"]
                    await f.write(f"#### {test_case_file}\n\n")
                    await f.write(f"**Input**: `{json.dumps(test_case.get('input', {}), ensure_ascii=False)}`\n\n")
                    await f.write(f"**Expected Output**: \n```json\n{json.dumps(test_case.get('expected_output', {}), ensure_ascii=False, indent=2)}\n```\n\n")
                    await f.write("**Actual Output**:\n```")
                    if result.get("stdout"):
                        await f.write(result["stdout"])
                    await f.write("```\n\n")
                    await f.write(f"- **Accuracy**: {analysis.get('accuracy', 0.0):.2f}%\n")
                    await f.write(f"- **Tool Usage**: {analysis.get('tool_usage', 'none')}\n")
                    await f.write(f"- **Required Content Match**: {analysis.get('required_content', 'none')}\n")
                    await f.write(f"- **Semantic Match**: {analysis.get('semantic_match', 'none')}\n\n")
                await f.write("---\n\n")

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

    parser.add_argument(
        "--embedding-model",
        default=None,
        help="Embedding model name or path (default: None, will use environment variable or default in processor)"
    )

    parser.add_argument(
        "--embedding-threshold",
        type=float,
        default=0.45,
        help="Embedding similarity threshold (default: None, will use environment variable or default in processor)"
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
            reports_dir=args.reports_dir,
            embedding_model_name_or_path=args.embedding_model,
            embedding_threshold=args.embedding_threshold
        )
        asyncio.run(runner.async_run_benchmark())
        return 0
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
