import time
import json
from typing import Generator, Dict, Any

def stream_simulation() -> Generator[Dict[str, Any], None, None]:
    # 1. Reasoning content output
    yield {
        "model": "qwen-plus-latest",
        "test_case": "test_case_chat",
        "reasoning_content": "hello world",
        "choice_delta": None,
        "tool_call": None,
        "memory_call": None,
        "usage": None
    }
    time.sleep(0.5)

    # 2. Text streaming output - first part
    yield {
        "model": "qwen-plus-latest",
        "test_case": "test_case_chat",
        "reasoning_content": None,
        "choice_delta": {
            "content": "hello",
            "finish_reason": None
        },
        "tool_call": None,
        "memory_call": None,
        "usage": None
    }
    time.sleep(0.5)

    # 3. Tool call output
    yield {
        "model": "qwen-plus-latest",
        "test_case": "test_case_chat",
        "reasoning_content": None,
        "choice_delta": None,
        "tool_call": {
            "instructions": "Check current weather conditions in Tokyo",
            "call_id": "1",
            "name": "get_weather",
            "arguments": {
                "location": "Tokyo"
            }
        },
        "usage": None
    }
    time.sleep(0.5)

    # 4. Text streaming output - second part
    yield {
        "model": "qwen-plus-latest",
        "test_case": "test_case_chat",
        "reasoning_content": None,
        "choice_delta": {
            "content": "world",
            "finish_reason": None
        },
        "tool_call": None,
        "memory_call": None,
        "usage": None
    }
    time.sleep(0.5)

    # 5. Stream end
    yield {
        "model": "qwen-plus-latest",
        "test_case": "test_case_chat",
        "reasoning_content": None,
        "choice_delta": {
            "content": None,
            "finish_reason": "stop"
        },
        "tool_call": None,
        "memory_call": None,
        "usage": None
    }
    time.sleep(0.5)

    # 6. Usage output
    yield {
        "model": "qwen-plus-latest",
        "test_case": "test_case_chat",
        "reasoning_content": None,
        "choice_delta": None,
        "tool_call": None,
        "memory_call": None,
        "usage": {
            "prompt_tokens": 723,
            "completion_tokens": 312,
            "total_tokens": 1035
        }
    }

def demo_stream():
    for response in stream_simulation():
        print(json.dumps(response, ensure_ascii=False))

if __name__ == "__main__":
    demo_stream()
