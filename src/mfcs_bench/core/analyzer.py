"""
Response analyzer for benchmark results
"""
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class ResponseAnalyzer:
    """Analyzes benchmark responses"""
    
    DEFAULT_ANALYSIS = {
        "tool_usage": "none",
        "required_content": "none",
        "semantic_match": "none",
        "accuracy": 0.0,
        "response_time": 0.0,
        "token_usage": {"prompt": 0, "completion": 0},
        "success": False,
        "model": "unspecified"
    }

    def _collect_response_data(self, responses: List[Dict[str, Any]]) -> tuple[List[str], List[str], str, List[Dict], Dict[str, int]]:
        """
        Collect and process response data
        
        Args:
            responses: List of response dictionaries
            
        Returns:
            Tuple containing:
            - all_content: List of content strings
            - all_reasoning_content: List of reasoning content strings
            - combined_content: Combined streamed content string
            - tool_calls: List of tool call dictionaries
            - token_usage: Dictionary of token usage
        """
        all_content = []
        all_reasoning_content = []
        streamed_content = []
        tool_calls = []
        token_usage = {"prompt": 0, "completion": 0}
        
        for response in responses:
            logger.info(f"Processing response: {response}")
            
            content = response.get("content", "")
            reasoning = response.get("reasoning_content", "")
            
            if response.get("choice_delta", {}).get("content"):
                delta_content = response["choice_delta"]["content"]
                if delta_content is not None:
                    streamed_content.append(delta_content)
            
            if content:
                all_content.append(content)
            if reasoning:
                all_reasoning_content.append(reasoning)
            
            tool_call = response.get("tool_call")
            if tool_call and tool_call.get("name"):
                tool_calls.append(tool_call)
            
            if response.get("usage"):
                token_usage["prompt"] += response["usage"].get("prompt_tokens", 0)
                token_usage["completion"] += response["usage"].get("completion_tokens", 0)
                
        combined_content = "".join(streamed_content) if streamed_content else ""
        
        return all_content, all_reasoning_content, combined_content, tool_calls, token_usage

    def _check_semantic_match(self, all_content: List[str], all_reasoning_content: List[str], 
                            combined_content: str, expected_match: str) -> bool:
        """
        Check if the semantic match exists in any content
        
        Args:
            all_content: List of content strings
            all_reasoning_content: List of reasoning content strings
            combined_content: Combined streamed content string
            expected_match: Expected semantic match string
            
        Returns:
            Boolean indicating if match was found
        """
        if not expected_match:
            return True
            
        all_text = []
        all_text.extend(all_content)
        all_text.extend(all_reasoning_content)
        if combined_content:
            all_text.append(combined_content)
        
        expected_match_lower = expected_match.lower()
        
        return any(expected_match_lower in text.lower() for text in all_text if text)

    def analyze_responses(self, responses: List[Dict[str, Any]], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the responses from a benchmark run
        
        Args:
            responses: List of response dictionaries
            test_case: Test case dictionary
            
        Returns:
            Analysis results dictionary
        """
        logger.info(f"Starting analysis with test case: {test_case}")
        
        analysis = self.DEFAULT_ANALYSIS.copy()
        
        # Get expected tool usage and semantic match
        expected_output = test_case.get("expected_output", {})
        expected_tool = expected_output.get("contains_tool")
        expected_semantic_match = expected_output.get("semantic_match", "")
        
        logger.info(f"Expected semantic match: {expected_semantic_match}")
        logger.info(f"Expected tool usage: {expected_tool}")
        
        # Process all responses first
        all_content, all_reasoning_content, combined_content, tool_calls, token_usage = self._collect_response_data(responses)
        
        logger.info(f"Collected content: {all_content}")
        logger.info(f"Collected reasoning content: {all_reasoning_content}")
        logger.info(f"Combined streamed content: {combined_content}")
        logger.info(f"Collected tool calls: {tool_calls}")
        logger.info(f"Token usage: {token_usage}")
        
        # Initialize success tracking
        success_count = 0
        total_checks = 0

        # Check tool usage match
        if expected_tool is not None:
            total_checks += 1
            tool_usage_success = False
            
            # Check all collected tool calls
            for tool_call in tool_calls:
                tool_name = tool_call.get("name", "")
                if tool_name == expected_tool:
                    tool_usage_success = True
                    analysis["tool_usage"] = tool_name
                    break
            
            logger.info(f"Tool usage check - Expected: {expected_tool}, Found: {analysis['tool_usage']}, Success: {tool_usage_success}")
            
            if tool_usage_success:
                success_count += 1
                logger.info("Tool usage check passed")
            else:
                logger.info("Tool usage check failed")

        # Check semantic match
        if expected_semantic_match:
            total_checks += 1
            # Check for semantic match in any response
            found_match = self._check_semantic_match(all_content, all_reasoning_content, combined_content, expected_semantic_match)
            
            logger.info(f"Semantic match check - Found: {found_match}")
            if found_match:
                analysis["semantic_match"] = "yes"
                success_count += 1
                logger.info("Semantic match check passed")
            else:
                logger.info("Semantic match check failed")

        # Calculate accuracy
        if total_checks > 0:
            # If all checks passed, set accuracy to 100%, otherwise 0%
            analysis["accuracy"] = 100.0 if success_count == total_checks else 0.0
            logger.info(f"Accuracy calculation - Success count: {success_count}, Total checks: {total_checks}, Accuracy: {analysis['accuracy']}%")
            
            # Set success flag based on accuracy
            analysis["success"] = success_count == total_checks
            logger.info(f"Success status: {analysis['success']} (all checks must pass)")
        else:
            # If no checks were performed, consider it successful
            analysis["accuracy"] = 100.0
            analysis["success"] = True
            logger.info("No checks performed, setting accuracy to 100%")

        logger.info(f"Final analysis: {analysis}")
        return analysis