from slips.slips_alert_monitor import SlipsAlertMonitor  # adjust to your file/module name
import time
import os


def handle_alert(alert_data: dict):
    print(f"[ALERT] {alert_data.get('ID')} - {alert_data.get('Description')}")
    print(alert_data)

path = os.path.expanduser("~/output/alerts.json")

monitor = SlipsAlertMonitor(
    alert_file_path=path,
    on_alert=handle_alert,
    start_from_end=False
)

try:
    monitor.start()
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    monitor.stop()
