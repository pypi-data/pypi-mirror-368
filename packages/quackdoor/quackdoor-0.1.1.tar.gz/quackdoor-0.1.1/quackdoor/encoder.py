"""
encoder.py

Utilities for encoding Python code in Base64 and generating executable command strings.

This module provides functions to:
- Convert raw Python code into a Base64-encoded string.
- Construct a `python3 -c` command that decodes and executes the encoded payload.
"""

import base64


def encode_payload(raw_code: str) -> str:
    """
    Encode a string of Python code using Base64.

    This function takes a raw Python code string, encodes it into bytes,
    then encodes those bytes using Base64 and returns the result as a UTF-8 string.

    Args:
        raw_code (str): The raw Python code to encode.

    Returns:
        str: The Base64-encoded string representation of the input code.
    """
    return base64.b64encode(raw_code.encode()).decode()


def build_python_exec_command(encoded: str) -> str:
    """
    Construct a shell command to execute Base64-encoded Python code.

    This function builds a command string that uses `python3 -c` to import
    the `base64` module and execute the decoded version of the provided Base64-encoded code.

    Args:
        encoded (str): The Base64-encoded Python code to decode and execute.

    Returns:
        str: A complete shell command that executes the encoded Python code.
    """
    return f"python3 -c \"import base64; exec(base64.b64decode('{encoded}'))\""
