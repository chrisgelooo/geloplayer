import os

def scan_directory(directory_path: str) -> list[str]:
    """
    Scans the given directory for files ending with the .mp3 extension.

    Args:
        directory_path: The path to the directory to scan.

    Returns:
        A list of full file paths to .mp3 files.
        Returns an empty list if the directory doesn't exist or other errors occur.
    """
    if not os.path.isdir(directory_path):
        print(f"Warning: Directory '{directory_path}' not found.")
        return []

    mp3_files = []
    try:
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path) and item.lower().endswith(".mp3"):
                mp3_files.append(os.path.abspath(item_path))
    except OSError as e:
        print(f"Error scanning directory '{directory_path}': {e}")
        return []
    return mp3_files
