"""
Core processor for benchmark results
"""
from typing import Dict, List, Any, TypedDict, Tuple
import json
import subprocess
import os
import time
import logging
from contextlib import contextmanager
from time import perf_counter
import sys

logger = logging.getLogger(__name__)

@contextmanager
def log_execution_time(operation: str):
    """Context manager to log execution time of operations"""
    start_time = perf_counter()
    try:
        yield
    finally:
        execution_time = perf_counter() - start_time
        logger.debug(f"{operation} completed in {execution_time:.2f} seconds")

class TokenUsage(TypedDict):
    prompt: int
    completion: int

class Analysis(TypedDict):
    tool_usage: str
    required_content: str
    semantic_match: str
    accuracy: float
    response_time: float
    token_usage: TokenUsage
    success: bool
    model: str

class BenchmarkProcessor:
    """Processes benchmark results and handles test execution"""

    DEFAULT_ANALYSIS: Analysis = {
        "tool_usage": "none",
        "required_content": "none",
        "semantic_match": "none",
        "accuracy": 0.0,
        "response_time": 0.0,
        "token_usage": {"prompt": 0, "completion": 0},
        "success": False,
        "model": "unspecified"
    }

    STREAM_CHECK_DELAY: float = 0.1
    PROCESS_POLL_DELAY: float = 0.1

    def __init__(self):
        """Initialize the processor"""
        pass

    def process_app(self, command: List[str], app_config: Dict[str, Any], app_name: str) -> Dict[str, Any]:
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
            # Use stream setting from config
            is_stream = app_config.get("stream", False)

            
                
            # Handle different command types
            if command[0] == 'python':
                # Get virtual environment path
                venv_path = os.environ.get('VIRTUAL_ENV')
                if venv_path:
                    # Add venv Scripts/bin directory to PATH
                    if sys.platform == 'win32':
                        scripts_dir = 'Scripts'
                        python_name = 'python.exe'
                    else:
                        scripts_dir = 'bin'
                        python_name = 'python'
                    
                    scripts_path = os.path.join(venv_path, scripts_dir)
                    # Use Python from venv directly
                    python_executable = os.path.join(scripts_path, python_name)
                    if not os.path.exists(python_executable):
                        logger.error(f"Python executable not found in virtual environment: {python_executable}")
                        raise FileNotFoundError(f"Python executable not found: {python_executable}")
                    command[0] = python_executable
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True
            )
            
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

    def _handle_stream_output(self, process: subprocess.Popen) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Handle streaming output from a process
        
        Args:
            process: Subprocess to handle output from
            
        Returns:
            Tuple containing stdout, stderr and parsed responses
        """
        stdout_data: List[str] = []
        stderr_data: List[str] = []
        responses: List[Dict[str, Any]] = []
        
        # Set timeout for stream reading (in seconds)
        timeout = 30
        start_time = time.time()
        
        while True:
            # Check for timeout
            if time.time() - start_time > timeout:
                logger.warning(f"Stream reading timed out after {timeout} seconds")
                process.terminate()
                break
                
            # Check if process has finished
            if process.poll() is not None:
                # Read any remaining output
                remaining_out, remaining_err = process.communicate()
                if remaining_out:
                    stdout_data.append(remaining_out)
                    for line in remaining_out.splitlines():
                        try:
                            if line.strip():
                                response = json.loads(line.strip())
                                responses.append(response)
                        except json.JSONDecodeError:
                            continue
                if remaining_err:
                    stderr_data.append(remaining_err)
                break

            # Read from stdout without blocking
            try:
                line = process.stdout.readline()
                if line:
                    stdout_data.append(line)
                    try:
                        if line.strip():
                            response = json.loads(line.strip())
                            responses.append(response)
                    except json.JSONDecodeError:
                        continue
                else:
                    # No more output
                    break
            except Exception as e:
                logger.error(f"Error reading stream: {e}")
                break

            # Read from stderr without blocking
            try:
                err_line = process.stderr.readline()
                if err_line:
                    stderr_data.append(err_line)
            except Exception:
                pass

        # Ensure process is terminated
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        return ''.join(stdout_data), ''.join(stderr_data), responses

    def _parse_responses(self, stdout: str) -> List[Dict[str, Any]]:
        """
        Parse responses from stdout
        
        Args:
            stdout: Standard output string to parse
            
        Returns:
            List of parsed response dictionaries
        """
        responses: List[Dict[str, Any]] = []
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

    def _load_test_case(self, app_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load test case from file
        
        Args:
            app_config: Application configuration dictionary
            
        Returns:
            Test case dictionary
        """
        logger.debug("Starting test case loading")
        test_case: Dict[str, Any] = {}
        try:
            test_case_path = next(
                (arg.split('=')[1] for arg in app_config["args"] if arg.startswith("--test_case_name=")),
                None
            )
            if test_case_path:
                test_case_full_path = os.path.join("test_cases", test_case_path)
                logger.debug(f"Loading test case from: {test_case_full_path}")
                with open(test_case_full_path, 'r', encoding='utf-8') as f:
                    test_case = json.load(f)
                logger.debug("Test case loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load test case: {e}", exc_info=True)
        return test_case

    def _analyze_responses(self, responses: List[Dict[str, Any]], test_case: Dict[str, Any]) -> Analysis:
        """
        Analyze responses
        
        Args:
            responses: List of response dictionaries
            test_case: Test case dictionary
            
        Returns:
            Analysis results
        """
        logger.debug("Starting response analysis")
        analysis = self.DEFAULT_ANALYSIS.copy()
        
        # Ensure test_case and responses are not None
        if test_case is None:
            test_case = {}
        if responses is None:
            responses = []
            
        expected_output = test_case.get("expected_output", {})
        has_tool_check = "contains_tool" in expected_output
        expected_tool = expected_output.get("contains_tool") if has_tool_check else None
        
        logger.debug(f"Expected tool check: {has_tool_check}, Expected tool: {expected_tool}")
        
        actual_tool_used = "none"
        is_stream = False
        token_usage = {"prompt": 0, "completion": 0}
        final_usage = None
        combined_content = []

        for idx, response in enumerate(responses):
            if not isinstance(response, dict):
                logger.warning(f"Skipping invalid response at index {idx}: {response}")
                continue
                
            logger.debug(f"Processing response {idx + 1}/{len(responses)}")
            
            # Safely get model
            model = response.get("model")
            if model:
                analysis["model"] = model
                logger.debug(f"Model identified: {model}")
            
            # Safely get tool_call
            tool_call = response.get("tool_call")
            if isinstance(tool_call, dict):
                tool_name = tool_call.get("name", "")
                if tool_name:
                    actual_tool_used = tool_name
                    logger.debug(f"Tool usage identified: {tool_name}")
            
            # Safely get various content
            content = response.get("content", "")
            reasoning_content = response.get("reasoning_content", "")
            choice_delta = response.get("choice_delta")
            delta_content = choice_delta.get("content") if isinstance(choice_delta, dict) else None
            
            if content:
                combined_content.append(str(content))
            if reasoning_content:
                combined_content.append(str(reasoning_content))
            if delta_content:
                combined_content.append(str(delta_content))
            
            # Detect if it is a streaming response
            if choice_delta is not None:
                is_stream = True
            
            # Safely handle token usage
            usage = response.get("usage")
            if isinstance(usage, dict):
                current_usage = usage
                final_usage = current_usage
                if is_stream:
                    token_usage["prompt"] += current_usage.get("prompt_tokens", 0)
                    token_usage["completion"] += current_usage.get("completion_tokens", 0)

        # Set final token usage
        if is_stream:
            analysis["token_usage"] = token_usage.copy()
        elif isinstance(final_usage, dict):
            analysis["token_usage"]["prompt"] = final_usage.get("prompt_tokens", 0)
            analysis["token_usage"]["completion"] = final_usage.get("completion_tokens", 0)
        
        logger.debug(f"Final token usage: {analysis['token_usage']}")

        # Check semantic match
        if "semantic_match" in expected_output:
            expected_match = str(expected_output.get("semantic_match", ""))
            all_content = "".join(combined_content)
            logger.debug(f"Combined content for matching: {all_content}")
            logger.debug(f"Expected match: {expected_match}")
            
            if expected_match and expected_match in all_content:
                analysis["semantic_match"] = "yes"
                logger.debug("Semantic match found")
            else:
                analysis["semantic_match"] = "no"
                logger.debug("Semantic match not found")

        # Set tool usage status
        if has_tool_check:
            if actual_tool_used == "none":
                analysis["tool_usage"] = "no"
            elif actual_tool_used == expected_tool:
                analysis["tool_usage"] = actual_tool_used
            else:
                analysis["tool_usage"] = "no"
        else:
            analysis["tool_usage"] = "none"
            
        logger.debug(f"Final tool usage status: {analysis['tool_usage']}")

        # Calculate accuracy
        metrics_to_compare = 0
        successful_metrics = 0
        
        if has_tool_check:
            metrics_to_compare += 1
            if analysis["tool_usage"] != "no":
                successful_metrics += 1
                logger.debug("Tool usage check passed")
            else:
                logger.debug("Tool usage check failed")
            
        if "semantic_match" in expected_output:
            expected_match = str(expected_output.get("semantic_match", ""))
            if expected_match != "none":
                metrics_to_compare += 1
                if analysis["semantic_match"] == "yes":
                    successful_metrics += 1
                    logger.debug("Semantic match check passed")
                else:
                    logger.debug("Semantic match check failed")

        if metrics_to_compare > 0:
            analysis["accuracy"] = (successful_metrics / metrics_to_compare) * 100.0
        else:
            analysis["accuracy"] = 100.0
            
        analysis["success"] = analysis["accuracy"] == 100.0
        
        logger.info(
            "Response analysis completed",
            extra={
                "accuracy": analysis["accuracy"],
                "success": analysis["success"],
                "metrics_compared": metrics_to_compare,
                "successful_metrics": successful_metrics,
                "tool_usage": analysis["tool_usage"],
                "semantic_match": analysis["semantic_match"],
                "token_usage": analysis["token_usage"]
            }
        )
        
        return analysis