"""
Core processor for benchmark results
"""
from typing import Dict, List, Any, Optional
import json
import subprocess
import os
import time
import select
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BenchmarkProcessor:
    """Processes benchmark results and handles test execution"""

    def __init__(self):
        """Initialize the processor"""
        pass

    def process_app(self, command: List[str], app_config: Dict, app_name: str) -> Dict[str, Any]:
        """
        Process a single application test
        
        Args:
            command: Command to execute
            app_config: Application configuration
            app_name: Name of the application
            
        Returns:
            Dictionary containing test results
        """
        try:
            start_time = time.time()
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Determine if streaming is needed
            is_stream = app_config.get("stream", None)
            
            if is_stream is None:
                try:
                    time.sleep(0.1)
                    if process.stdout and select.select([process.stdout], [], [], 0.0)[0]:
                        is_stream = True
                    else:
                        is_stream = False
                except Exception:
                    is_stream = False
            
            if is_stream:
                stdout, stderr, responses = self._handle_stream_output(process)
            else:
                stdout, stderr = process.communicate()
                responses = self._parse_responses(stdout)
            
            end_time = time.time()
            
            # Load test case
            test_case = self._load_test_case(app_config)
            
            # Analyze responses
            analysis = self._analyze_responses(responses, test_case)
            
            result = {
                "app_name": app_name,
                "success": analysis["success"],
                "stdout": stdout,
                "stderr": stderr,
                "execution_time": end_time - start_time,
                "return_code": process.returncode,
                "is_stream": is_stream,
                "analysis": analysis,
                "test_case": test_case,
                "responses": responses
            }

            # Add helper methods as properties
            result["get_model_name"] = lambda: analysis.get("model", test_case.get("model", "unspecified"))
            result["get_accuracy"] = lambda: analysis.get("accuracy", 0.0)
            result["get_tool_usage"] = lambda: analysis.get("tool_usage", "none")
            result["get_semantic_match"] = lambda: analysis.get("semantic_match", "no")
            result["get_token_usage"] = lambda: analysis.get("token_usage", {"prompt": 0, "completion": 0})
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process application: {e}")
            test_case = self._load_test_case(app_config)
            
            return {
                "app_name": app_name,
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "is_stream": False,
                "analysis": {
                    "tool_usage": "none",
                    "required_content": False,
                    "semantic_match": "no",
                    "accuracy": 0.0,
                    "response_time": 0.0,
                    "token_usage": {"prompt": 0, "completion": 0},
                    "model": test_case.get("model", "unspecified")
                },
                "test_case": test_case,
                "responses": []
            }

    def _handle_stream_output(self, process: subprocess.Popen) -> tuple[str, str, List[Dict]]:
        """Handle streaming output from a process"""
        stdout_data = []
        stderr_data = []
        responses = []
        
        # Set non-blocking mode
        for pipe in [process.stdout, process.stderr]:
            if pipe:
                os.set_blocking(pipe.fileno(), False)
        
        while True:
            if process.poll() is not None:
                break

            if process.stdout:
                while True:
                    try:
                        line = process.stdout.readline()
                        if not line:
                            break
                        stdout_data.append(line)
                        try:
                            response = json.loads(line.strip())
                            responses.append(response)
                        except json.JSONDecodeError:
                            pass
                    except (IOError, BlockingIOError):
                        break

            if process.stderr:
                while True:
                    try:
                        line = process.stderr.readline()
                        if not line:
                            break
                        stderr_data.append(line)
                    except (IOError, BlockingIOError):
                        break

            time.sleep(0.1)

        # Read any remaining output
        if process.stdout:
            remaining_stdout = process.stdout.read()
            if remaining_stdout:
                stdout_data.append(remaining_stdout)
        if process.stderr:
            remaining_stderr = process.stderr.read()
            if remaining_stderr:
                stderr_data.append(remaining_stderr)

        return ''.join(stdout_data), ''.join(stderr_data), responses

    def _parse_responses(self, stdout: str) -> List[Dict]:
        """Parse responses from stdout"""
        responses = []
        try:
            if stdout.strip():
                response = json.loads(stdout.strip())
                responses.append(response)
        except json.JSONDecodeError:
            for line in stdout.splitlines():
                try:
                    if line.strip():
                        response = json.loads(line.strip())
                        responses.append(response)
                except json.JSONDecodeError:
                    continue
        return responses

    def _load_test_case(self, app_config: Dict) -> Dict:
        """Load test case from file"""
        test_case = {}
        try:
            test_case_path = next(
                (arg.split('=')[1] for arg in app_config["args"] if arg.startswith("--test_case_name=")),
                None
            )
            if test_case_path:
                test_case_full_path = os.path.join("test_cases", test_case_path)
                with open(test_case_full_path, 'r', encoding='utf-8') as f:
                    test_case = json.load(f)
        except Exception:
            pass
        return test_case

    def _analyze_responses(self, responses: List[Dict], test_case: Dict) -> Dict[str, Any]:
        """Analyze responses"""
        analysis = {
            "tool_usage": "none",
            "required_content": False,
            "semantic_match": "no",
            "accuracy": 0.0,
            "response_time": 0.0,
            "token_usage": {"prompt": 0, "completion": 0},
            "success": False,
            "model": "unspecified"
        }
        
        for response in responses:
            # Get model name
            if response.get("model"):
                analysis["model"] = response["model"]
            
            # Check tool usage
            if response.get("tool_call"):
                tool_name = response["tool_call"].get("name", "")
                analysis["tool_usage"] = tool_name
                if "expected_tool" in test_case and tool_name == test_case["expected_tool"]:
                    analysis["accuracy"] = 100.0
                    analysis["success"] = True
            
            # Check semantic match
            if "semantic_match" in test_case.get("expected_output", {}):
                expected_match = test_case["expected_output"]["semantic_match"]
                content = response.get("content", "")
                reasoning_content = response.get("reasoning_content", "")
                
                # Check both content and reasoning_content for semantic match
                if (content and expected_match in content) or \
                   (reasoning_content and expected_match in reasoning_content):
                    analysis["semantic_match"] = "yes"
            
            # Accumulate token usage
            if response.get("usage"):
                analysis["token_usage"]["prompt"] += response["usage"].get("prompt_tokens", 0)
                analysis["token_usage"]["completion"] += response["usage"].get("completion_tokens", 0)

        return analysis 

    def get_summary_stats(self, results: List[Dict]) -> Dict[str, Any]:
        """
        Get summary statistics from results
        
        Args:
            results: List of test results
            
        Returns:
            Dictionary containing summary statistics
        """
        return {
            "total_apps": len(results),
            "successful_apps": sum(1 for r in results if r["success"]),
            "failed_apps": sum(1 for r in results if not r["success"]),
            "total_execution_time": sum(r["execution_time"] for r in results),
            "average_accuracy": sum(r["analysis"].get("accuracy", 0.0) for r in results) / max(len(results), 1),
            "tool_usage_rate": sum(1 for r in results if r["analysis"].get("tool_usage", "none") != "none") / max(len(results), 1) * 100,
            "semantic_match_rate": sum(1 for r in results if r["analysis"].get("semantic_match", "no") == "yes") / max(len(results), 1) * 100
        }

    def get_test_case_info(self, result: Dict) -> Dict[str, Any]:
        """
        Get formatted test case information
        
        Args:
            result: Test result dictionary
            
        Returns:
            Dictionary containing formatted test case information
        """
        test_case = result.get("test_case", {})
        return {
            "name": result["analysis"].get("test_case", "unknown"),
            "description": test_case.get("description", ""),
            "input": test_case.get("input", {}),
            "expected_output": test_case.get("expected_output", {}),
            "actual_output": result.get("stdout", "")
        } 