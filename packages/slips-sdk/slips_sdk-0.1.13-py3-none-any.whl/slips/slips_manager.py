import subprocess
import shlex
import os
from typing import List, Optional


class SlipsManager:
    """
    A Python SDK for managing the StratosphereLinuxIPS (SLIPS) binary via subprocess.
    Provides methods to start SLIPS, query version, clear cache, stop daemon, and more.

    This manager resolves paths relative to the SDK file location and ensures compatibility
    with SLIPS dependencies like the VERSION file or config YAML.
    """

    def __init__(self):
        """
        Initialize the SlipsManager with resolved binary and config paths
        relative to the current script location.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # print(f"[INFO] Base directory for SLIPS SDK: {base_dir}")

        # Paths resolved relative to this SDK file
        self.binary_path = os.path.abspath(os.path.join(base_dir, "StratosphereLinuxIPS", "slips.py"))
        # self.default_config = os.path.join(base_dir, "StratosphereLinuxIPS", "config", "slips.yaml")
        self.default_config = "/etc/slips-sdk/config/slips.yaml"

        # print(f"[INFO] SLIPS binary path: {self.binary_path}")
        # print(f"[INFO] SLIPS default config path: {self.default_config}")
        # self.db_files = os.path.join(base_dir, "etc", "slips-sdk", "databases", "macaddress-db.json")
        self.db_files = "/etc/slips-sdk/databases/macaddress-db.json"


        if not os.path.isfile(self.binary_path):
            raise FileNotFoundError(f"SLIPS binary not found at {self.binary_path}")
        
        if not os.access(self.binary_path, os.X_OK):
            try:
                subprocess.run(["chmod", "+x", self.binary_path], check=True)
                # print(f"[INFO] Made slips.py executable: {self.binary_path}")
            except subprocess.CalledProcessError as e:
                raise PermissionError(f"Failed to make binary executable: {e}")

        if not os.access(self.db_files, os.X_OK):
            try:
                subprocess.run(["touch", self.db_files ])
                # print(f"[INFO] create the db file : {self.db_files}")
            except subprocess.CalledProcessError as e:
                raise PermissionError(f"Failed to create db file : {e}")

    def _run_command(self, args: List[str], capture_output: bool = False) -> subprocess.CompletedProcess:
        """
        Internal helper to run SLIPS command with arguments using subprocess.

        Args:
            args (List[str]): List of command-line arguments to pass to SLIPS.
            capture_output (bool): If True, captures stdout and stderr.

        Returns:
            subprocess.CompletedProcess: The result of the subprocess run.

        Raises:
            CalledProcessError if command fails.
        """
        command = ["sudo", "python3", self.binary_path] + args
        # command_str = " ".join(shlex.quote(str(arg)) for arg in command)
        # print(f"[SLIPS CMD] {command_str}")
# 
        return subprocess.run(
            command,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
            cwd=os.path.dirname(self.binary_path),  # Important for relative files like VERSION
            check=True
        )
    
    def start(self,
            file: Optional[str] = None,
            file_name: Optional[str] = None,
            dataset_path: Optional[str] = None,
            interface: Optional[str] = None,
            output_dir: Optional[str] = None,
            verbose: int = 0,
            debug: int = 0,
            blocking: bool = False,
            daemon: bool = False,
            save: bool = False,
            growing: bool = False,
            pcap_filter: Optional[str] = None):
        """
        Start SLIPS with a combination of CLI parameters.

        Args:
            file (str): Absolute path to PCAP or Zeek logs. Overrides dataset_path + file_name.
            file_name (str): File name to be used with dataset_path.
            dataset_path (str): Path to the dataset directory (default is SLIPS dataset dir).
            interface (str): Network interface to listen on.
            output_dir (str): Directory to store logs/output.
            verbose (int): Verbosity level.
            debug (int): Debug level.
            blocking (bool): Enable IP blocking (iptables).
            daemon (bool): Run SLIPS in daemon mode.
            save (bool): Save analysis DB.
            growing (bool): Treat input folder as growing.
            pcap_filter (str): BPF-style filter string.
        """
        args = ["-c", self.default_config]

        if file:
            args += ["-f", os.path.expanduser(file)]
        elif file_name:
            if not dataset_path:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                # dataset_path = os.path.join(base_dir, "dataset")
                dataset_path = "/etc/slips-sdk/dataset"
            full_file_path = os.path.expanduser(os.path.join(dataset_path, file_name))
            if not os.path.isfile(full_file_path):
                raise FileNotFoundError(f"Dataset file not found: {full_file_path}")
            args += ["-f", full_file_path]

        if interface:
            args += ["-i", interface]
        if output_dir:
            args += ["-o", os.path.expanduser(output_dir)]
        if verbose:
            args += ["-v", str(verbose)]
        if debug:
            args += ["-e", str(debug)]
        if blocking:
            args.append("-p")
        if daemon:
            args.append("-D")
        if save:
            args.append("-s")
        if growing:
            args.append("-g")
        if pcap_filter:
            args += ["-F", pcap_filter]

        return self._run_command(args)

    def stop_daemon(self):
        """
        Stop SLIPS if running in daemon mode.
        """
        return self._run_command(["-S"])

    def kill_all_redis(self):
        """
        Kill all unused Redis servers started by SLIPS.
        """
        return self._run_command(["-k"])

    def start_multi_instance(self):
        """
        Run SLIPS in multi-instance mode without overwriting older runs.
        """
        return self._run_command(["-c", self.default_config, "-m"])

    def get_version(self) -> str:
        """
        Get the SLIPS version.

        Returns:
            str: Version string.
        """
        result = self._run_command(["-V"], capture_output=True)
        return result.stdout.decode().strip()

    def clear_blocking_chain(self):
        """
        Remove iptables blocking rules set by SLIPS.
        """
        return self._run_command(["-cb"])

    def clear_cache(self):
        """
        Clear the SLIPS cache database.
        """
        return self._run_command(["-cc"])

    def test_mode(self):
        """
        Run SLIPS in test mode for unit testing or dry runs.
        """
        return self._run_command(["-c", self.default_config, "-t"])

    def start_web_interface(self):
        """
        Start the SLIPS web interface module.
        """
        return self._run_command(["-c", self.default_config, "-w"])


# Example usage
# if __name__ == "__main__":
#     slips = SlipsManager()

#     try:
#         print("Version:", slips.get_version())
#         slips.start(file="test.pcap", verbose=1, debug=1, output_dir="~/output")
#     except Exception as e:
#         print(f"[ERROR] {e}")
