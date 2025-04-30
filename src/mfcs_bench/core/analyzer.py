"""
Response analyzer for benchmark results
"""
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class ResponseAnalyzer:
    """Analyzes benchmark responses"""

    def analyze_responses(self, responses: List[Dict], test_case: Dict) -> Dict[str, Any]:
        """
        Analyze the responses from a benchmark run
        
        Args:
            responses: List of response dictionaries
            test_case: Test case dictionary
            
        Returns:
            Analysis results dictionary
        """
        analysis = {
            "tool_usage": "none",
            "required_content": "none",
            "semantic_match": "none",
            "accuracy": 0.0,
            "response_time": 0.0,
            "token_usage": {"prompt": 0, "completion": 0},
            "success": False,
            "model": "unspecified"
        }
        
        # Get expected tool usage and semantic match
        expected_output = test_case.get("expected_output", {})
        expected_tool_usage = expected_output.get("contains_tool", False)
        expected_semantic_match = expected_output.get("semantic_match", "")
        
        success_factors = []
        total_factors = 0
        semantic_match_success = False
        tool_usage_success = False
        
        for response in responses:
            # Get model name
            if response.get("model"):
                analysis["model"] = response["model"]
            
            # Check tool usage
            has_tool_call = response.get("tool_call") is not None
            if has_tool_call:
                analysis["tool_usage"] = "yes"
            elif not expected_tool_usage:
                # If tool usage is not expected and not used, consider it correct
                analysis["tool_usage"] = "yes"
            
            # Check if tool usage matches expectation
            if "contains_tool" in expected_output:
                tool_usage_success = expected_tool_usage == has_tool_call
                if tool_usage_success:
                    success_factors.append(1)
                total_factors += 1
            
            # Check semantic match
            if expected_semantic_match:
                reasoning_content = response.get("reasoning_content", "")
                content = response.get("content", "")
                if (content and expected_semantic_match in content) or \
                   (reasoning_content and expected_semantic_match in reasoning_content):
                    analysis["semantic_match"] = "yes"
                    semantic_match_success = True
                    success_factors.append(1)
                total_factors += 1
            
            # Accumulate token usage
            if response.get("usage"):
                analysis["token_usage"]["prompt"] += response["usage"].get("prompt_tokens", 0)
                analysis["token_usage"]["completion"] += response["usage"].get("completion_tokens", 0)

        # Check if there are any evaluation requirements
        has_tool_requirement = "contains_tool" in expected_output
        has_semantic_requirement = bool(expected_semantic_match)
        has_any_requirement = has_tool_requirement or has_semantic_requirement

        # Calculate accuracy and success status
        if not has_any_requirement:
            # If there are no evaluation requirements, add a default success factor
            success_factors.append(1)
            total_factors += 1
        
        # Calculate overall accuracy
        if total_factors > 0:
            analysis["accuracy"] = (sum(success_factors) / total_factors) * 100.0
        
        # Set success flag
        # If there are no requirements, consider it successful
        if not has_any_requirement:
            analysis["success"] = True
        else:
            # If semantic match is required, it must be satisfied
            semantic_match_success = analysis["semantic_match"] == "yes" if has_semantic_requirement else True
            
            # If tool usage is required, it must match expectation
            tool_usage_success = expected_tool_usage == has_tool_call if has_tool_requirement else True
            
            # Only consider successful if all required conditions are met
            analysis["success"] = semantic_match_success and tool_usage_success

        return analysis