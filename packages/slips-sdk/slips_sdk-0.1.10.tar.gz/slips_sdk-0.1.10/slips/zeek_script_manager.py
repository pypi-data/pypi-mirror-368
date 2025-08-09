import os
from typing import List


class ZeekScriptManager:
    """
    SDK to manage Zeek script files within a dedicated directory.

    Features:
    - Upload a new Zeek script from any path
    - List all available Zeek script filenames
    - View the content of a specific script
    - Edit existing script content
    - Delete a script
    - Check file existence

    Note:
    The absolute path of the script directory is kept private to avoid exposure.
    """

    def __init__(self, directory: str = "/etc/slips-sdk/zeek-scripts"):
        """
        Initialize the ZeekScriptManager.

        Parameters:
            directory (str): Relative path from this file to the Zeek script storage directory.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # self._script_dir = os.path.abspath(os.path.join(base_dir, directory))
        self._script_dir = directory
        os.makedirs(self._script_dir, exist_ok=True)

    def list_scripts(self) -> List[str]:
        """
        List all Zeek script filenames in the storage directory.

        Returns:
            List[str]: Sorted list of script filenames.
        """
        return sorted([
            f for f in os.listdir(self._script_dir)
            if os.path.isfile(os.path.join(self._script_dir, f))
        ])

    def upload_script(self, source_path: str, new_name: str = None) -> str:
        """
        Upload a script file to the Zeek script directory.

        Parameters:
            source_path (str): Path to the source file on disk.
            new_name (str, optional): Optional new name to store the script as.

        Returns:
            str: The filename used for the uploaded script.

        Raises:
            FileNotFoundError: If the source file does not exist.
        """
        if not os.path.isfile(source_path):
            raise FileNotFoundError("Source file does not exist.")

        filename = new_name if new_name else os.path.basename(source_path)
        dest_path = os.path.join(self._script_dir, filename)

        with open(source_path, "rb") as src_file, open(dest_path, "wb") as dst_file:
            dst_file.write(src_file.read())

        return filename

    def read_script(self, filename: str) -> str:
        """
        Read the content of a specific Zeek script.

        Parameters:
            filename (str): Name of the script file to read.

        Returns:
            str: The content of the script file.

        Raises:
            FileNotFoundError: If the file does not exist in the directory.
        """
        file_path = os.path.join(self._script_dir, filename)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Script '{filename}' not found.")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def edit_script(self, filename: str, content: str) -> None:
        """
        Overwrite the content of an existing script file.

        Parameters:
            filename (str): Name of the script to edit.
            content (str): New content to write to the file.

        Raises:
            FileNotFoundError: If the target script does not exist.
        """
        file_path = os.path.join(self._script_dir, filename)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Script '{filename}' not found for editing.")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def delete_script(self, filename: str) -> bool:
        """
        Delete a Zeek script by filename.

        Parameters:
            filename (str): Name of the script to delete.

        Returns:
            bool: True if deletion was successful, False if file did not exist.
        """
        file_path = os.path.join(self._script_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def file_exists(self, filename: str) -> bool:
        """
        Check if a script exists in the Zeek script directory.

        Parameters:
            filename (str): Name of the script file to check.

        Returns:
            bool: True if file exists, False otherwise.
        """
        return os.path.isfile(os.path.join(self._script_dir, filename))
