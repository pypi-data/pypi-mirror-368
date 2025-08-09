from slips.dataset_manager import DatasetManager

# Initialize manager — path will resolve to StratosphereLinuxIPS/dataset relative to this script
manager = DatasetManager()

print("\n📁 Listing all dataset items:")
print(manager.list_items())

print("\n📥 Uploading sample.pcap...")
manager.upload("/tmp/sample_dataset/sample.pcap")

print("\n📥 Uploading local Zeek logs as 'test-new-zeek'...")
manager.upload("/tmp/sample_dataset/local_zeek_dir", new_name="test-new-zeek")

print("\n📄 Reading first 5 lines of 'test10-mixed-zeek-dir/conn.log':")
try:
    lines = manager.read_file("test10-mixed-zeek-dir/conn.log", max_lines=5)
    print("\n".join(lines))
except FileNotFoundError:
    print("conn.log not found in test10-mixed-zeek-dir")

print("\n🧾 Metadata for 'test10-mixed-zeek-dir':")
try:
    meta = manager.get_metadata("test10-mixed-zeek-dir")
    print(meta)
except FileNotFoundError:
    print("Directory not found: test10-mixed-zeek-dir")

print("\n✅ Checking if 'test10-mixed-zeek-dir' exists:")
print("Exists:", manager.exists("test10-mixed-zeek-dir"))

print("\n🔄 Replacing conn.log inside 'test10-mixed-zeek-dir' with new_conn.log...")
manager.update("/tmp/sample_dataset/new_conn.log", "test10-mixed-zeek-dir/conn.log")

print("\n📄 Confirm updated conn.log content:")
try:
    lines = manager.read_file("test10-mixed-zeek-dir/conn.log", max_lines=3)
    print("\n".join(lines))
except FileNotFoundError:
    print("conn.log not found after update")

# print("\n🗑️ Deleting 'test-new-zeek' dataset...")
# deleted = manager.delete("test-new-zeek")
# print("Deleted:", deleted)

print("\n✅ Final dataset list:")
print(manager.list_items())
