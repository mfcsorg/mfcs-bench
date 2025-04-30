var response = {
    "model": "qwen-plus-latest",
    "test_case": "test_case_chat",
    "reasoning_content": "hello world",
    "content": "hello world",
    "tool_call": {
        "instructions": "Check current weather conditions in Tokyo",
        "call_id": "1",
        "name": "get_weather",
        "arguments": {
            "location": "Tokyo"
        }
    },
    "usage": {
        "prompt_tokens": 723,
        "completion_tokens": 312,
        "total_tokens": 1035
    }
};

console.log(JSON.stringify(response, null, 2));
