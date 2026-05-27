import argparse
from json import tool
import os
import anthropic

client = anthropic.Anthropic()
SYSTEM_PROMPT = """
            You are a file analysis agent. You have access to tools for executing Python code and reading files. Your job is to complete the user's task by using these tools step by step.

            Guidelines:
            - Think briefly about what you need to do, then call a tool.
            - After receiving each tool result, decide the next action.
            - When the task is complete, provide a final answer and stop calling tools.
            - If a tool returns an error, try a different approach rather than repeating the same call.
            - Keep your reasoning concise.
        """
INITIAL_TASK = "Find the largest file in the specified directory."

TOOLS = [
    {
        "name": "execute_python",
        "description": (
            "Executes Python code in a sandboxed subprocess and returns "
            "stdout and stderr. Use this for file system operations "
            "(listing directories, checking file sizes), calculations, "
            "and data inspection. Code runs in a fresh interpreter each "
            "call — variables do not persist between calls. Output is "
            "truncated at 5000 characters."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": (
                        "Python code to execute. Must be a complete, "
                        "self-contained snippet. Use print() to return values."
                    )
                }
            },
            "required": ["code"]
        }
    },
    {
        "name": "read_file",
        "description": (
            "Reads the contents of a text file and returns it as a string. "
            "Returns the first 5000 characters if the file is larger. "
            "Returns an error message if the file does not exist or cannot "
            "be read as text."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read, relative or absolute."
                }
            },
            "required": ["path"]
        }
    }
]

def read_file(path):
    """
    Reads the contents of a text file and returns it as a string.

    Args:
        path (str): The path to the file to read.
    """
    try:
        with open(path, 'r') as file:
            content = file.read()
            return content[:5000]  # Return first 5000 characters
    except Exception as e:
        return f"Error reading file: {e}"

def execute_tool(name, tool_input):
    """
    Executes a specified tool with the given input.

    Args:
        name (str): The name of the tool to execute.
        tool_input (dict): The input parameters for the tool.

    Returns:
        str: The result of the tool execution.
    """
    if name == "execute_python":
        code = tool_input.get("code", "")
        try:
            # Execute the Python code in a sandboxed environment
            exec_globals = {}
            exec(code, exec_globals)
            return exec_globals.get("result", "No result returned.")
        except Exception as e:
            return f"Error executing Python code: {e}"
    elif name == "read_file":
        path = tool_input.get("path", "")
        try:
            with open(path, 'r') as file:
                content = file.read()
                return content[:5000]  # Return first 5000 characters
        except Exception as e:
            return f"Error reading file: {e}"
    else:
        return f"Unknown tool: {name}"

def largest_file_finder(max_iter: int, directory: str) -> None:
    """
    Finds the largest file in the specified directory.

    Args:
        initial_task (str): The initial task or directory path to search.
        max_iter (int): The maximum number of iterations to perform.
        directory (str): The path to the directory to search.
    """

    messages = [{"role": "user", "content" : INITIAL_TASK + f" Directory: {directory}"}]
    for i in range(max_iter):
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=TOOLS,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            final = next((b.text for b in response.content if b.type == "text"), "")
            print(f"FINAL ANSWER: {final}")
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"[tool call] {block.name} with input: {block.input}")
                    result = execute_tool(block.name, block.input)
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": result}
                    )
            messages.append({"role": "user", "content": tool_results})
            continue

def llm_loop(api_token: str):
    """
    Main loop for the LLM (Large Language Model) interaction.
    This function continuously prompts the user for input, processes it,
    and generates responses using the LLM until the user decides to exit.
    """
    print(f"Using API key: {api_token[:5]}...{api_token[-5:]}" if api_token else "No API key supplied")
    # Placeholder for actual LLM interaction logic.


def parse_args():
    parser = argparse.ArgumentParser(description="Run phase0 LLM loop with a supplied API key")
    parser.add_argument(
        "--api-key",
        "-k",
        dest="api_key",
        help="API key for the LLM service",
    )
    parser.add_argument(
        "--model",
        "-m",
        default=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
        help="Optional model name override",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=int(os.getenv("MAX_ITERATIONS", "6")),
        help="Maximum number of loop iterations",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    api_key = args.api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        api_key = input("Enter your API key: ")

    print(f"Model: {args.model}")
    print(f"Max iterations: {args.max_iterations}")
    llm_loop(api_key)
    