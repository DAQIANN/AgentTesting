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