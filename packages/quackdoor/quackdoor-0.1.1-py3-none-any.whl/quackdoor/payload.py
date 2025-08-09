"""
payload.py

Provides a utility function for reading payload files as strings.
"""


def read_payload(file_path: str) -> str:
    """
    Read and return the contents of a text file as a stripped string.

    This function opens the file at the specified path, reads its entire content,
    strips leading and trailing whitespace (including newlines), and returns the result.

    Args:
        file_path (str): Path to the payload file to be read.

    Returns:
        str: The stripped contents of the file as a single string.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {file_path}") from e
    except PermissionError as e:
        raise PermissionError(f"Permission denied when accessing: {file_path}") from e
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            "utf-8", b"", 0, 1, f"File is not UTF-8 encoded: {file_path}"
        ) from e
    except OSError as e:
        raise OSError(f"Failed to read file {file_path}: {e}") from e
