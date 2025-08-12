from typing import List

from folder_classifier.dto import Folder


def flatten_folder(folder: Folder, parent_path: str = "") -> List[str]:
    """
    Traverses a Folder and returns a list of file paths.
    Each path is constructed by joining folder and file names with '/'.
    """
    paths: List[str] = []
    # Build the path for the current folder
    current_path = f"{parent_path}/{folder.name}" if parent_path else folder.name

    for item in folder.items:
        if item.type == "file":
            paths.append(f"{current_path}/{item.name}")
        else:
            # Recursively flatten subfolders
            paths.extend(flatten_folder(item, current_path))
    return paths