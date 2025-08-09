import os
import shutil
from typing import List, Dict, Union
from datetime import datetime

class DatasetManager:
    """
    SDK to manage datasets (files or directories) in a structured dataset folder.
    """

    def __init__(self, directory: str = "/etc/slips-sdk/dataset"):
        """
        Initialize the DatasetManager with a given directory (relative to the script location).
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # self.dataset_root = os.path.abspath(os.path.join(base_dir, directory))
        self.dataset_root = directory
        os.makedirs(self.dataset_root, exist_ok=True)

    def list_items(self) -> List[str]:
        """List all files and folders in the dataset directory."""
        return sorted(os.listdir(self.dataset_root))

    def upload(self, source_path: str, new_name: str = None) -> str:
        """
        Upload a file or directory into the dataset folder.
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError("Source path does not exist.")

        target_name = new_name or os.path.basename(source_path)
        target_path = os.path.join(self.dataset_root, target_name)

        if os.path.exists(target_path):
            raise FileExistsError("Target already exists.")

        if os.path.isdir(source_path):
            shutil.copytree(source_path, target_path)
        else:
            shutil.copy2(source_path, target_path)

        return target_path

    def read_file(self, relative_path: str, max_lines: int = 100) -> List[str]:
        """Read the contents of a file inside the dataset."""
        file_path = os.path.join(self.dataset_root, relative_path)
        if not os.path.isfile(file_path):
            raise FileNotFoundError("File does not exist.")
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return [line.strip() for _, line in zip(range(max_lines), f)]

    def update(self, source_path: str, name: str) -> str:
        """Replace an existing dataset item with a new file or folder."""
        target_path = os.path.join(self.dataset_root, name)
        if os.path.exists(target_path):
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
        return self.upload(source_path, name)

    def delete(self, name: str) -> bool:
        """Delete a dataset item."""
        target_path = os.path.join(self.dataset_root, name)
        if os.path.exists(target_path):
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
            return True
        return False

    def exists(self, name: str) -> bool:
        """Check if a dataset item exists."""
        return os.path.exists(os.path.join(self.dataset_root, name))

    def get_metadata(self, name: str) -> Dict[str, Union[str, int]]:
        """Get metadata about a dataset file or folder."""
        path = os.path.join(self.dataset_root, name)
        if not os.path.exists(path):
            raise FileNotFoundError("Item not found.")

        return {
            "name": name,
            "type": "directory" if os.path.isdir(path) else "file",
            "size_bytes": self._get_size(path),
            "created": datetime.fromtimestamp(os.path.getctime(path)).isoformat(),
            "modified": datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
        }

    def _get_size(self, path: str) -> int:
        """Get size of file or folder."""
        if os.path.isfile(path):
            return os.path.getsize(path)
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total += os.path.getsize(fp)
        return total

    def get_data_set_path(self):
        return self.dataset_root