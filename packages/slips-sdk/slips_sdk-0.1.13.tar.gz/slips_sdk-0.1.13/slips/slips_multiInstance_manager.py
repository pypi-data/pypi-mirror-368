import subprocess
import shlex
import os
import signal
import json
from typing import Optional, List
from datetime import datetime


class SlipsMultiInstanceManager:
    """
    Enhanced manager to run and manage multiple SLIPS daemon processes.
    Supports:
    - Multi-instance mode
    - Port separation
    - Output directory isolation
    - PID tracking and process termination
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.binary_path = os.path.join(self.base_dir, "StratosphereLinuxIPS/slips.py")
        self.default_config = os.path.join(self.base_dir, "/etc/slips-sdk/config/slips.yaml")
        self.pid_dir = os.path.join(self.base_dir, "slips_pids")

        if not os.path.isfile(self.binary_path):
            raise FileNotFoundError(f"SLIPS binary not found at {self.binary_path}")

        os.makedirs(self.pid_dir, exist_ok=True)

    def _build_command(self, config: str, port: int, output_dir: str, file: Optional[str],
                       interface: Optional[str], verbose: int, debug: int,
                       blocking: bool, save: bool, growing: bool, pcap_filter: Optional[str]) -> List[str]:

        args = [self.binary_path, "-c", config, "-m", "-P", str(port), "-o", output_dir]

        if file:
            args += ["-f", file]
        if interface:
            args += ["-i", interface]
        if verbose:
            args += ["-v", str(verbose)]
        if debug:
            args += ["-e", str(debug)]
        if blocking:
            args.append("-p")
        if save:
            args.append("-s")
        if growing:
            args.append("-g")
        if pcap_filter:
            args += ["-F", pcap_filter]

        return args

    def start_instance(self, instance_name: str, port: int, file: Optional[str] = None, interface: Optional[str] = None,
                       verbose: int = 0, debug: int = 0, blocking: bool = False, save: bool = False,
                       growing: bool = False, pcap_filter: Optional[str] = None):
        """
        Start a new SLIPS instance with unique port/output.
        Stores PID and metadata under slips_pids/instance_name.json
        """
        output_dir = os.path.join(self.base_dir, f"output_{instance_name}")
        os.makedirs(output_dir, exist_ok=True)

        command = self._build_command(
            config=self.default_config,
            port=port,
            output_dir=output_dir,
            file=file,
            interface=interface,
            verbose=verbose,
            debug=debug,
            blocking=blocking,
            save=save,
            growing=growing,
            pcap_filter=pcap_filter
        )

        # print("[SLIPS MULTI-START]", " ".join(shlex.quote(arg) for arg in command))
        process = subprocess.Popen(
            command,
            cwd=os.path.dirname(self.binary_path),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Store process metadata
        meta = {
            "pid": process.pid,
            "instance_name": instance_name,
            "port": port,
            "output_dir": output_dir,
            "start_time": datetime.utcnow().isoformat()
        }
        with open(os.path.join(self.pid_dir, f"{instance_name}.json"), "w") as f:
            json.dump(meta, f, indent=2)

        return meta

    def stop_instance(self, instance_name: str):
        """
        Stop a running SLIPS instance by name using its PID.
        """
        pid_file = os.path.join(self.pid_dir, f"{instance_name}.json")
        if not os.path.exists(pid_file):
            raise FileNotFoundError(f"Instance metadata not found: {pid_file}")

        with open(pid_file) as f:
            meta = json.load(f)
            pid = meta.get("pid")

        try:
            os.kill(pid, signal.SIGTERM)
            os.remove(pid_file)
            # print(f"[STOPPED] Instance '{instance_name}' (PID: {pid})")
        except ProcessLookupError:
            # print(f"[WARNING] Process {pid} not found. Cleaning up.")
            os.remove(pid_file)

    def list_instances(self):
        """
        List all currently tracked SLIPS daemon instances.
        """
        instances = []
        for fname in os.listdir(self.pid_dir):
            if fname.endswith(".json"):
                with open(os.path.join(self.pid_dir, fname)) as f:
                    instances.append(json.load(f))
        return instances

    def stop_all_instances(self):
        """
        Stop all running tracked instances.
        """
        for instance in self.list_instances():
            self.stop_instance(instance["instance_name"])
