import os
import subprocess
import sys
import slips  # This is required to locate the installed module

def is_root():
    return os.geteuid() == 0

def main():
    # Locate the installed path of the 'slips' module
    slips_path = os.path.dirname(slips.__file__)
    
    # Navigate to the StratosphereLinuxIPS path
    target_dir = os.path.join(slips_path, "StratosphereLinuxIPS")
    install_script = os.path.join(target_dir, "install", "install.sh")

    if not os.path.exists(install_script):
        print(f"[slips-setup] install.sh not found at: {install_script}")
        sys.exit(1)

    if not is_root():
        print("[ERROR] install.sh requires root permissions.")
        print("Please run this command using sudo:")
        print("\n  sudo slips-setup\n")
        sys.exit(1)

    try:
        print(f"[slips-setup] Changing directory to: {target_dir}")
        os.chdir(target_dir)

        print("[slips-setup] Executing: sudo bash install/install.sh")
        subprocess.check_call(["bash", "install/install.sh"])
        print("[slips-setup] install.sh executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[slips-setup] install.sh failed with exit code {e.returncode}")
        sys.exit(e.returncode)
