from slips.zeek_script_manager import ZeekScriptManager

manager = ZeekScriptManager()

# Upload a file
manager.upload_script("/tmp/my_scan.zeek")

# Edit content
manager.edit_script("my_scan.zeek", "# updated script\nprint(\"Updated\")")

# Read content
print(manager.read_script("my_scan.zeek"))

# List available scripts
print(manager.list_scripts())

# Delete
# manager.delete_script("my_scan.zeek")
