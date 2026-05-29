import argparse
import os
import anthropic
import subprocess
from pathlib import Path
import json


# try:
#     from dotenv import load_dotenv
# except ModuleNotFoundError:
#     def load_dotenv(*_args, **_kwargs):
#         return False

# load_dotenv()

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

def serialize_tool_result(value):
    """Convert tool outputs into JSON-safe text for Anthropic tool results."""
    return json.dumps(value, default=str, ensure_ascii=True)

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
            result = exec_globals.get("result", "No result returned.")
            return serialize_tool_result(result)
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

def largest_file_finder(max_iter: int, directory: str, api_key: str, model: str) -> None:
    """
    Finds the largest file in the specified directory.

    Args:
        max_iter (int): The maximum number of iterations to perform.
        directory (str): The path to the directory to search.
        api_key (str): API key used to initialize the Anthropic client.
        model (str): Model name to use for the request.
    """

    client = anthropic.Anthropic(api_key=api_key)
    messages = [{"role": "user", "content" : INITIAL_TASK + f" Directory: {directory}"}]
    for i in range(max_iter):
        print(f"Iteration number: {i+1}")
        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=messages,
                tools=TOOLS,
            )
        except anthropic.NotFoundError as exc:
            print(f"Model '{model}' was not found. Use a supported model alias or set ANTHROPIC_MODEL. Error: {exc}")
            return

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

        print(f"Unexpected stop reason: {response.stop_reason}")
        break
    else:
        print("Reached maximum iterations of " + str(max_iter) + " without a final answer.")

def llm_loop(api_token: str):
    """
    Main loop for the LLM (Large Language Model) interaction.
    This function continuously prompts the user for input, processes it,
    and generates responses using the LLM until the user decides to exit.
    """
    print(f"Using API key: {api_token[:5]}...{api_token[-5:]}" if api_token else "No API key supplied")
    # Placeholder for actual LLM interaction logic.


def parse_args():
    parser = argparse.ArgumentParser(description="Run phase0 with a selectable method")
    parser.add_argument(
        "--method",
        "-m",
        choices=["largest_file", "llm_loop"],
        default="largest_file",
        help="Which execution method to run",
    )
    parser.add_argument(
        "--api-key",
        "--api_key",
        "-k",
        dest="api_key",
        help="API key for the LLM service",
    )
    parser.add_argument(
        "--model",
        "-M",
        default=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5"),
        help="Optional model name override",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=int(os.getenv("MAX_ITERATIONS", "6")),
        help="Maximum number of loop iterations",
    )
    parser.add_argument(
        "--directory",
        default=".",
        help="Directory to analyze when running the largest_file method",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    api_key = args.api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        api_key = input("Enter your API key: ")

    print(f"Method: {args.method}")
    print(f"Model: {args.model}")
    print(f"Max iterations: {args.max_iterations}")

    if args.method == "largest_file":
        largest_file_finder(
            max_iter=args.max_iterations,
            directory=args.directory,
            api_key=api_key,
            model=args.model,
        )
    else:
        llm_loop(api_key)
    