import inspect
from pathlib import Path
from IPython import get_ipython


def get_calling_script_file_path(print_debug_info=False):
    """
    Get the file path of the script that called this function.
    Handles cases where the function is called from an installed package.

    Args:
        print_debug_info (bool): If True, prints debug information about the call stack.

    Returns:
        str: The file path of the calling script, or the current working directory as a fallback.
    """
    stack = inspect.stack()

    # Debugging: Print the stack for inspection
    if print_debug_info:
        print("Debug Info: Full stack trace:")
        for frame in stack:
            print(f"  Frame: {frame.function}, File: {frame.filename}")

    # Find the first frame that is not part of the Python system or site-packages
    for frame in stack:
        if "site-packages" not in frame.filename and "python" not in frame.filename:
            if print_debug_info:
                print(f"Debug Info: Found calling script: {frame.filename}")
            return str(Path(frame.filename).resolve())

    # Fallback: Return the current working directory
    if print_debug_info:
        print(
            "Debug Info: No valid calling script found. Falling back to current working directory."
        )
    return str(Path.cwd())


def get_root_directory(print_debug_info=False):
    """
    Determines the root directory based on the execution environment.

    - If running in a Jupyter notebook, returns the current working directory.
    - Otherwise, returns the directory of the script containing this function.

    Args:
        print_debug_info (bool): If True, prints debug information.

    Returns:
        str: The root directory.
    """
    # Check if running in a Jupyter notebook
    if "get_ipython" in globals() and hasattr(get_ipython(), "config"):
        if print_debug_info:
            print("Debug Info: Running in a Jupyter notebook. Returning current working directory.")
        return str(Path.cwd())

    # Use the calling script's file path
    calling_script_path = get_calling_script_file_path(print_debug_info)
    return str(Path(calling_script_path).parent)


def here(path="", print_debug_info=False):
    """
    Resolves a path relative to the root directory.

    Args:
        path (str): A string representing the relative path to resolve.
        print_debug_info (bool): If True, prints debug information.

    Returns:
        str: The resolved full path.
    """
    root_directory = Path(get_root_directory(print_debug_info))
    resolved_path = root_directory.joinpath(*path.split("/")).resolve()
    if print_debug_info:
        print(f"Debug Info: Resolving path '{path}' relative to root directory '{root_directory}'.")
        print(f"Debug Info: Resolved path is '{resolved_path}'.")
    return str(resolved_path)


if __name__ == "__main__":
    # Example usage
    print("File Working Directory:", get_root_directory(print_debug_info=True))
    print()
    print("Resolved Path of subfolders data/output:", here("data/output", print_debug_info=True))
    print()
    print(
        "Resolved Path with config folder parallel to Parent:",
        here("../config", print_debug_info=True),
    )
