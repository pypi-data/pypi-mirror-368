# test_mixed_tools.py

import json
import os
import shutil
from pathlib import Path
from openai import OpenAI
from agents.mcp.server import MCPServerStdio, MCPServerSse
from agentd.patch import patch_openai_with_mcp
from agentd.tool_decorator import tool


@tool
def add_numbers(x: int, y: int) -> int:
    """
    Add two integers.

    x: first addend
    y: second addend
    """
    return x + y

@tool
def greet(name: str) -> str:
    """
    Return a greeting.

    name: person’s name
    """
    return f"Hello, {name}!"

env = os.environ.copy()
nvm_bin = os.path.expanduser("~/.nvm/versions/node/v22.16.0/bin")
env["PATH"] = nvm_bin + os.pathsep + env.get("PATH", "")

fs_server = MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp/"],
        "env": env
    },
    cache_tools_list=True,
)

remote_server = MCPServerSse(
    params={
        "url": "https://my-mcp.example.com/v1",
        "headers": {"Authorization": "Bearer sk-foo"},
        "timeout": 10,
    },
    cache_tools_list=True
)

# This is an explicit schema that the model can choose to call. By default,
# our patch will detect it and bubble back the function_call so we must
# supply a local execution path if we want to handle it in-process.
explicit_tool_schema = {
    "type": "function",
    "function": {
        "name": "multiply_numbers",
        "description": "Multiply two integers and return the product.",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"}
            },
            "required": ["x", "y"]
        }
    }
}

# Provide a matching Python function so that if the patched client chooses
# to run this in-process (i.e. "explicit with local implementation"), it will succeed.
def multiply_numbers(x: int, y: int) -> int:
    return x * y

# Register it in the function registry so the patch can find it
from agentd.tool_decorator import FUNCTION_REGISTRY
FUNCTION_REGISTRY["multiply_numbers"] = multiply_numbers

def print_response(label, response):
    """Helper to print out content or function_call, whichever is present."""
    # For responses API, check output for text content
    output = getattr(response, 'output', [])
    
    for item in output:
        if getattr(item, 'type', None) == 'message':
            content = getattr(item, 'content', [])
            for content_item in content:
                if getattr(content_item, 'type', None) == 'output_text':
                    print(f"\n[{label}] Assistant says:\n{content_item.text}")
                    return
    
    print(f"\n[{label}] No text output found. Output: {output}")

def test_decorator_only():
    """
    No mcp_servers, no explicit tools → uses only @tool-registered functions:
      - add_numbers
      - greet
    """
    client = patch_openai_with_mcp(OpenAI())
    print("\n=== Test: Decorator-Only ===")
    input = "What is add_numbers(10, 5)? Then greet 'Alice'."
    response = client.responses.create(
        model="gpt-4o-mini",
        #model="gemini/gemini-2.0-flash",
        input=input
    )
    print_response("Decorator-Only", response)

def test_fs_mcp_only():
    """
    mcp_servers=[fs_server], no explicit tools:
      - Uses filesystem MCP tool (e.g. `list_dir /tmp`)
      - Also still includes decorator tools, but here we ask only for FS action
    """
    client = patch_openai_with_mcp(OpenAI())
    print("\n=== Test: Filesystem MCP Only ===")
    input = "List files in '/tmp/' using the filesystem tool."
    response = client.responses.create(
        #model="gemini/gemini-2.0-flash",
        model="gpt-4o-mini",
        input=input,
        mcp_servers=[fs_server],
        mcp_strict=True
    )
    print_response("FS-MCP-Only", response)

def test_explicit_local_only():
    """
    tools=[explicit_tool_schema], no mcp_servers:
      - Supplies only the explicit 'multiply_numbers' schema
      - Since we provided a local function multiply_numbers, it should run in-process
    """
    client = patch_openai_with_mcp(OpenAI())
    print("\n=== Test: Explicit-Local Only ===")
    input = "Use multiply_numbers to multiply 7 and 8."
    response = client.responses.create(
        model="gpt-4o-mini",
        #model="gemini/gemini-2.0-flash",
        input=input,
        tools=[explicit_tool_schema]
    )
    print_response("Explicit-Local-Only", response)

def test_all_three_combined():
    """
    Use all three together:
      - tools=[explicit_tool_schema]
      - mcp_servers=[fs_server, remote_server]
      - Implicitly includes decorator tools (add_numbers, greet)
      The model can pick among:
        • multiply_numbers (explicit + local)
        • FS tools (from fs_server)
        • Remote tools (from remote_server)
        • add_numbers, greet (local decorator)
    """
    client = patch_openai_with_mcp(OpenAI())
    print("\n=== Test: All Three Combined ===")
    input = (
        "First, multiply 3 and 5 using multiply_numbers. "
        "Then list '/tmp/' via filesystem MCP. "
        "Finally, greet 'Bob' using the local greet function."
    )
    response = client.responses.create(
        model="gemini/gemini-2.0-flash",
        #model="gpt-4o-mini",
        input=input,
        tools=[explicit_tool_schema],
        mcp_servers=[fs_server],
        mcp_strict=False
    )
    print_response("All-Three-Combined", response)

if __name__ == "__main__":
    # Ensure /tmp/ has something inside for FS tool to list
    open("/tmp/test_file.txt", "w").write("hello")
    open("/tmp/test_dir_indicator", "w").write("dir")
    os.makedirs("/tmp/test_dir", exist_ok=True)

    test_decorator_only()
    
    try:
        test_fs_mcp_only()
    except Exception as e:
        print(f"\n[FS-MCP-Only] Failed with error: {e}")
    
    test_explicit_local_only()
    
    try:
        test_all_three_combined()
    except Exception as e:
        print(f"\n[All-Three-Combined] Failed with error: {e}")
