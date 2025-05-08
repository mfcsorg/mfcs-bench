import argparse
import asyncio
import json
import os
import sys
from typing import AsyncGenerator, Dict, Any
from mfcs import MemoryCall, ToolCall
from openai import AsyncOpenAI
from mfcs.response_parser import ResponseParser
from mfcs.function_prompt import FunctionPromptGenerator

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_test_case(test_cases_dir: str, test_case_name: str) -> Dict[str, Any]:
    """Load test case from JSON file"""
    test_case_path = os.path.join(test_cases_dir, test_case_name)
    with open(test_case_path, 'r', encoding='utf-8') as f:
        return json.load(f)

async def stream_llm_response(client: AsyncOpenAI, 
                            model: str,
                            model_config: Dict[str, Any],
                            messages: list,
                            test_case: str,
                            tools: list = None) -> AsyncGenerator[Dict[str, Any], None]:
    """Stream responses from OpenAI API"""
    
    # Initialize MFCS components
    parser = ResponseParser()
    
    # Generate function prompt using MFCS if tools are provided
    if tools:
        function_prompt = FunctionPromptGenerator.generate_function_prompt(tools)
        messages = [{"role": "system", "content": function_prompt}] + messages
    
    # Configure the API call parameters
    params = {
        "model": model,
        "messages": messages,
        "stream": True,
        "stream_options": {"include_usage": True}
    }

    try:
        # Make the API call
        stream = await client.chat.completions.create(**params)
        async for delta, call_info, reasoning_content, usage in parser.parse_stream_output(stream):
            # Initialize response structure
            response = {
                "model": model_config.get("name"),
                "test_case": test_case,
                "reasoning_content": reasoning_content,
                "choice_delta": None,
                "tool_call": None,
                "memory_call": None,
                "usage": None
            }

            if delta:
                response["choice_delta"] = {
                    "content": delta.content,
                    "finish_reason": delta.finish_reason
                }

            if call_info and isinstance(call_info, ToolCall):
                response["tool_call"] = {
                    "instructions": call_info.instructions,
                    "name": call_info.name,
                    "call_id": call_info.call_id,
                    "arguments": call_info.arguments
                }
            
            if call_info and isinstance(call_info, MemoryCall):
                response["memory_call"] = {
                    "instructions": call_info.instructions,
                    "name": call_info.name,
                    "memory_id": call_info.memory_id,
                    "arguments": call_info.arguments
                }
            
            if usage:
                response["usage"] = {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }

            yield response
    except Exception as e:
        print(f"Error during streaming: {str(e)}")
        raise

async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Path to model config file")
    parser.add_argument("--model_name", required=True, help="Name of the model to use")
    parser.add_argument("--tools", required=True, help="Path to tools config file")
    parser.add_argument("--tools_index", type=int, default=-1, help="Index of tools to use")
    parser.add_argument("--test_cases", required=True, help="Path to test cases directory")
    parser.add_argument("--test_case_name", required=True, help="Name of test case file")
    args = parser.parse_args()

    # Ensure UTF-8 encoding for stdout
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

    # Load configurations
    model_config_all = load_config(args.model)
    model_config = model_config_all.get(args.model_name)
    if model_config is None:
        print(f"[Error] Model name '{args.model_name}' not found in {args.model}.", file=sys.stderr)
        sys.exit(1)
    tools_config = load_config(args.tools)
    if not tools_config:
        print(f"[Error] Tools config is empty or not found in {args.tools}.", file=sys.stderr)
        sys.exit(1)
    test_case = load_test_case(args.test_cases, args.test_case_name)
    if not test_case:
        print(f"[Error] Test case '{args.test_case_name}' not found in {args.test_cases}.", file=sys.stderr)
        sys.exit(1)

    # Initialize OpenAI client
    client = AsyncOpenAI(
        api_key=model_config.get("api_key"),
        base_url=model_config.get("api_base")
    )

    # Prepare messages and tools
    messages = [{"role": "user", "content": test_case.get("input").get("user")}]

    # If tools_index is provided, use the specific tool
    if args.tools_index >= 0:
        tools = [tools_config[args.tools_index]]
    else:
        tools = tools_config

    # Stream responses
    async for response in stream_llm_response(
        client=client,
        model=args.model_name,
        model_config=model_config,
        messages=messages,
        test_case=args.test_case_name,
        tools=tools
    ):
        print(json.dumps(response, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
