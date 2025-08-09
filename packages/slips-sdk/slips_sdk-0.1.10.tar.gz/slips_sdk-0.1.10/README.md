# slips-sdk

[![PyPI version](https://badge.fury.io/py/slips-sdk.svg)](https://badge.fury.io/py/slips-sdk)
[![Python Version](https://img.shields.io/pypi/pyversions/slips-sdk.svg)](https://pypi.org/project/slips-sdk/)
[![License](https://img.shields.io/pypi/l/slips-sdk.svg)](https://pypi.org/project/slips-sdk/)

**Description:** SDK for interacting with slips IDS components  
**Python Requires:** >=3.10  
**Operating System:** Ubuntu 22.04  

---

## Installation

Install the SDK via pip:

```bash
sudo pip install slips-sdk
sudo slips-setup
```

---

## Quick Start

```python
from slips.slips_manager import SlipsManager

# Initialize the SLIPS manager
slips = SlipsManager()

# Get SLIPS version
print(slips.get_version())

# Start SLIPS with a pcap file and verbose output
slips.start(file="test.pcap", verbose=1, debug=1, output_dir="~/output")
```

---

## Usage

### SlipsManager

Manages the SLIPS binary via subprocess calls.

**Key Methods:**

- `start(file=None, interface=None, output_dir=None, verbose=0, debug=0, blocking=False, daemon=False, save=False, growing=False, pcap_filter=None)`  
  Start SLIPS with various options.

- `stop_daemon()`  
  Stop SLIPS daemon.

- `kill_all_redis()`  
  Kill all unused Redis servers started by SLIPS.

- `get_version()`  
  Returns the SLIPS version string.

- `clear_cache()`  
  Clear SLIPS cache database.

**Example:**

```python
from slips.slips_manager import SlipsManager

slips = SlipsManager()
print(slips.get_version())
slips.start(file="capture.pcap", verbose=2)
```

---

### Configuration Management Classes

Located in `slips.config` module, these classes manage SLIPS configuration files and credentials.

- `IDSConfig`
- `IrisConfig`
- `WardenConfig`
- `WhitelistConfig`
- `VTAPIKeyManager`
- `SlackBotTokenManager`
- `TIFeedManager`
- `SSLFeedManager`
- `RiskIQCredentialsManager`
- `JA3FeedManager`
- `LogstashConfigManager`
- `RedisConfManager`

**Example:**

```python
from slips.config import IDSConfig, VTAPIKeyManager

ids_config = IDSConfig()
print(ids_config.get_verbose())
ids_config.set_verbose(3)

vt_manager = VTAPIKeyManager()
vt_manager.set_key("your_api_key")
print(vt_manager.get_key())
```

---

### ZeekScriptManager

Manages Zeek script files.

**Example:**

```python
from slips.zeek_script_manager import ZeekScriptManager

manager = ZeekScriptManager()
print(manager.list_scripts())
manager.upload_script("/path/to/script.zeek")
content = manager.read_script("script.zeek")
print(content)
```

---

### DatasetManager

Manages datasets in a structured folder.

**Example:**

```python
from slips.dataset_manager import DatasetManager

dataset_mgr = DatasetManager()
print(dataset_mgr.list_items())
dataset_mgr.upload("/path/to/data.pcap")
metadata = dataset_mgr.get_metadata("data.pcap")
print(metadata)
```

---

## Documentation

For detailed API documentation, please refer to the source code in the `slips/` directory or the official documentation website (if available).

---

## License

slips‑sdk is licensed under the GNU Affero General Public License v3.0.  
See the [LICENSE](./LICENSE) file for details.