# # run_slips.py
from slips.slips_manager import SlipsManager

def main():
    slips = SlipsManager()

    try:
        print("SLIPS Version:", slips.get_version())
        slips.start(interface="eth0", verbose=1, debug=1, output_dir="~/output")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()


# ========================= USEING DEMON METHOD ==========================


# from slips.slips_manager import SlipsManager

# slips = SlipsManager()

# try:
#     slips.start(interface="eth0", output_dir="~/output", daemon=True, verbose=1, debug=1)
#     print("[INFO] SLIPS is running in daemon mode.")
# except Exception as e:
#     print(f"[ERROR] {e}")


# ========================= STOP Demone =================================


# from slips.slips_manager import SlipsManager

# slips = SlipsManager()

# try:
#     result = slips.stop_daemon()
#     print("[INFO] SLIPS daemon stopped successfully.")
# except Exception as e:
#     print(f"[ERROR] Failed to stop daemon: {e}")
