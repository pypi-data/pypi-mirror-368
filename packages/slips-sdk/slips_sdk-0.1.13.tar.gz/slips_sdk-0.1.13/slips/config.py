import os
import re
import yaml
import json
from typing import Any, List, Dict, Optional


class IDSConfig:
    """
    Configuration manager for slips.yaml.
    Provides get/set access with automatic saving and documentation.
    """

    def __init__(self, relative_path: str = "/etc/slips-sdk/config/slips.yaml"):
        self.config_path = relative_path
        self._data = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found at: {self.config_path}")
        with open(self.config_path, 'r') as f:
            self._data = yaml.safe_load(f)

    def _save(self):
        with open(self.config_path, 'w') as f:
            yaml.dump(self._data, f, default_flow_style=False)

    def _get(self, section: str, key: str, default: Any = None) -> Any:
        return self._data.get(section, {}).get(key, default)

    def _set(self, section: str, key: str, value: Any):
        if section not in self._data or not isinstance(self._data[section], dict):
            self._data[section] = {}
        self._data[section][key] = value
        self._save()

    # ---------------------- Modes ----------------------

    def get_logsfile(self):
        """Return the default output file for logs."""
        return self._get("modes", "logsfile")

    def set_logsfile(self, value):
        """Set the logs file path."""
        self._set("modes", "logsfile", value)

    # ---------------------- Parameters ----------------------

    def get_analysis_direction(self):
        """Get direction of traffic analysis: 'out' for outgoing or 'all' for full."""
        return self._get("parameters", "analysis_direction")

    def set_analysis_direction(self, value):
        """Set analysis direction (out/all)."""
        self._set("parameters", "analysis_direction", value)

    def get_label(self):
        """Return label for flow tagging: 'normal', 'malicious', etc."""
        return self._get("parameters", "label")

    def set_label(self, value):
        """Set the flow label for training or tagging."""
        self._set("parameters", "label", value)

    def get_verbose(self):
        """Get verbosity level for detection logs."""
        return self._get("parameters", "verbose")

    def set_verbose(self, value):
        """Set verbosity level (integer)."""
        self._set("parameters", "verbose", value)

    def get_debug(self):
        """Get debug level for internal tracing."""
        return self._get("parameters", "debug")

    def set_debug(self, value):
        """Set debug level (integer)."""
        self._set("parameters", "debug", value)

    def get_rotation(self):
        """Check if zeek log rotation is enabled."""
        return self._get("parameters", "rotation")

    def set_rotation(self, value: bool):
        """Enable or disable zeek log rotation."""
        self._set("parameters", "rotation", value)

    def get_tcp_inactivity_timeout(self):
        """Return TCP inactivity timeout in minutes (used by Zeek)."""
        return self._get("parameters", "tcp_inactivity_timeout")

    def set_tcp_inactivity_timeout(self, value: int):
        """Set Zeek TCP inactivity timeout in minutes."""
        self._set("parameters", "tcp_inactivity_timeout", value)

    def get_client_ips(self):
        """Return list of client IPs considered as local in analysis."""
        return self._get("parameters", "client_ips")

    def set_client_ips(self, ip_list):
        """Set list of client IPs for local network context."""
        self._set("parameters", "client_ips", ip_list)

    # ---------------------- FlowMLDetection ----------------------

    def get_flowml_mode(self):
        """Get ML detection mode: 'train' or 'test'."""
        return self._get("flowmldetection", "mode")

    def set_flowml_mode(self, value: str):
        """Set flow-based ML detection mode ('train' or 'test')."""
        self._set("flowmldetection", "mode", value)

    # ---------------------- ThreatIntelligence ----------------------

    def get_ti_update_period(self):
        """Return update interval (in seconds) for threat intel files."""
        return self._get("threatintelligence", "TI_files_update_period")

    def set_ti_update_period(self, seconds: int):
        """Set how often threat intel files are updated."""
        self._set("threatintelligence", "TI_files_update_period", seconds)

    def get_ti_wait_flag(self):
        """Return flag to wait for threat intelligence before analysis."""
        return self._get("threatintelligence", "wait_for_TI_to_finish")

    def set_ti_wait_flag(self, value: bool):
        """Set whether to wait for TI files before starting detection."""
        self._set("threatintelligence", "wait_for_TI_to_finish", value)

    def get_all_config(self):
        """Return the entire parsed configuration dictionary."""
        return self._data


class IrisConfig:
    """
    SDK for reading and updating iris_config.yaml.
    Provides structured access to each section.
    """

    def __init__(self, relative_path: str = "/etc/slips-sdk/config/iris_config.yaml"):
        self.config_path = relative_path
        self._data = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, 'r') as f:
            self._data = yaml.safe_load(f) or {}

    def _save(self):
        with open(self.config_path, 'w') as f:
            yaml.dump(self._data, f, default_flow_style=False)

    def _get(self, section: str, key: str, default: Any = None) -> Any:
        return self._data.get(section, {}).get(key, default)

    def _set(self, section: str, key: str, value: Any):
        if section not in self._data or not isinstance(self._data[section], dict):
            self._data[section] = {}
        self._data[section][key] = value
        self._save()

    # ---------------------- Identity ----------------------

    def get_generate_new_key(self) -> bool:
        return self._get("Identity", "GenerateNewKey")

    def set_generate_new_key(self, value: bool):
        self._set("Identity", "GenerateNewKey", value)

    # ---------------------- Server ----------------------

    def get_server_host(self) -> str:
        return self._get("Server", "Host")

    def set_server_host(self, value: str):
        self._set("Server", "Host", value)

    def get_server_port(self) -> int:
        return self._get("Server", "Port")

    def set_server_port(self, value: int):
        self._set("Server", "Port", value)

    def get_dht_server_mode(self) -> str:
        return self._get("Server", "DhtServerMode")

    def set_dht_server_mode(self, value: str):
        self._set("Server", "DhtServerMode", value)

    # ---------------------- Redis ----------------------

    def get_redis_host(self) -> str:
        return self._get("Redis", "Host")

    def set_redis_host(self, value: str):
        self._set("Redis", "Host", value)

    def get_redis_port(self) -> int:
        return self._get("Redis", "Port")

    def set_redis_port(self, value: int):
        self._set("Redis", "Port", value)

    def get_redis_channel(self) -> str:
        return self._get("Redis", "Tl2NlChannel")

    def set_redis_channel(self, value: str):
        self._set("Redis", "Tl2NlChannel", value)

    # ---------------------- PeerDiscovery ----------------------

    def get_disable_bootstrap_nodes(self) -> bool:
        return self._get("PeerDiscovery", "DisableBootstrappingNodes")

    def set_disable_bootstrap_nodes(self, value: bool):
        self._set("PeerDiscovery", "DisableBootstrappingNodes", value)

    def get_peer_multiaddresses(self) -> List[str]:
        return self._get("PeerDiscovery", "ListOfMultiAddresses", [])

    def set_peer_multiaddresses(self, addresses: List[str]):
        self._set("PeerDiscovery", "ListOfMultiAddresses", addresses)

    # ---------------------- Full Access ----------------------

    def get_all_config(self) -> dict:
        """Return entire config dictionary."""
        return self._data

    def save(self):
        """Manually save current in-memory data to file."""
        self._save()


class WardenConfig:
    """
    SDK for reading and updating warden.conf (JSON format).
    Expects the file to be in the same directory as this script.
    """

    def __init__(self, filename: str = "/etc/slips-sdk/config/warden.conf"):
        self.config_path = filename
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Warden config file not found: {self.config_path}")
        with open(self.config_path, "r") as f:
            self._data = json.load(f)

    def _save(self):
        with open(self.config_path, "w") as f:
            json.dump(self._data, f, indent=4)

    def _get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def _set(self, key: str, value: Any):
        self._data[key] = value
        self._save()

    # ---------------------- Top-Level Fields ----------------------

    def get_url(self) -> str:
        return self._get("url")

    def set_url(self, value: str):
        self._set("url", value)

    def get_certfile(self) -> str:
        return self._get("certfile")

    def set_certfile(self, value: str):
        self._set("certfile", value)

    def get_keyfile(self) -> str:
        return self._get("keyfile")

    def set_keyfile(self, value: str):
        self._set("keyfile", value)

    def get_cafile(self) -> str:
        return self._get("cafile")

    def set_cafile(self, value: str):
        self._set("cafile", value)

    def get_timeout(self) -> int:
        return self._get("timeout")

    def set_timeout(self, value: int):
        self._set("timeout", value)

    def get_name(self) -> str:
        return self._get("name")

    def set_name(self, value: str):
        self._set("name", value)

    # ---------------------- Nested Fields: errlog ----------------------

    def get_errlog_file(self) -> str:
        return self._get("errlog", {}).get("file")

    def set_errlog_file(self, path: str):
        if "errlog" not in self._data:
            self._data["errlog"] = {}
        self._data["errlog"]["file"] = path
        self._save()

    def get_errlog_level(self) -> str:
        return self._get("errlog", {}).get("level")

    def set_errlog_level(self, level: str):
        if "errlog" not in self._data:
            self._data["errlog"] = {}
        self._data["errlog"]["level"] = level
        self._save()

    # ---------------------- Nested Fields: filelog ----------------------

    def get_filelog_file(self) -> str:
        return self._get("filelog", {}).get("file")

    def set_filelog_file(self, path: str):
        if "filelog" not in self._data:
            self._data["filelog"] = {}
        self._data["filelog"]["file"] = path
        self._save()

    def get_filelog_level(self) -> str:
        return self._get("filelog", {}).get("level")

    def set_filelog_level(self, level: str):
        if "filelog" not in self._data:
            self._data["filelog"] = {}
        self._data["filelog"]["level"] = level
        self._save()

    # ---------------------- Utility Methods ----------------------

    def get_all_config(self) -> Dict[str, Any]:
        """Return the full parsed config dictionary."""
        return self._data.copy()

    def save(self):
        """Manually save any changes to disk."""
        self._save()


class WhitelistConfig:
    """
    SDK for managing whitelist.conf used by Slips.
    Supports listing, adding, updating, deleting, and saving whitelist IoC entries.
    """

    def __init__(self, filename: str = "/etc/slips-sdk/config/whitelist.conf"):
        # self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        self.config_path = filename
        self.header_lines = []
        self.entries: List[Dict[str, str]] = []
        self._load()

    def _load(self):
        self.header_lines = []
        self.entries = []

        with open(self.config_path, "r") as f:
            for line in f:
                striped = line.strip()
                if not striped or striped.startswith((";", "#")) or striped.startswith('"IoCType"'):
                    self.header_lines.append(line)
                    continue
                parts = [p.strip().strip('"') for p in striped.split(",")]
                if len(parts) == 4:
                    self.entries.append({
                        "IoCType": parts[0],
                        "IoCValue": parts[1],
                        "Direction": parts[2],
                        "IgnoreType": parts[3]
                    })

    def _save(self):
        with open(self.config_path, "w") as f:
            f.writelines(self.header_lines)
            for entry in self.entries:
                line = f'{entry["IoCType"]},{entry["IoCValue"]},{entry["Direction"]},{entry["IgnoreType"]}\n'
                f.write(line)

    # ------------------ Public Methods ------------------

    def list_whitelist(self) -> List[Dict[str, str]]:
        """Return all active whitelist entries."""
        return self.entries.copy()

    def find_entry(self, ioc_value: str) -> Optional[Dict[str, str]]:
        """Find an entry by IoCValue."""
        for entry in reversed(self.entries):  # last one takes precedence
            if entry["IoCValue"] == ioc_value:
                return entry
        return None

    def add_entry(self, ioc_type: str, ioc_value: str, direction: str, ignore_type: str):
        """Add a new entry or override an existing one with the same IoCValue."""
        self.entries = [e for e in self.entries if e["IoCValue"] != ioc_value]
        self.entries.append({
            "IoCType": ioc_type,
            "IoCValue": ioc_value,
            "Direction": direction,
            "IgnoreType": ignore_type
        })
        self._save()

    def update_entry(self, ioc_value: str, direction: Optional[str] = None, ignore_type: Optional[str] = None):
        """Update direction or ignore_type of an existing entry."""
        found = self.find_entry(ioc_value)
        if found:
            if direction:
                found["Direction"] = direction
            if ignore_type:
                found["IgnoreType"] = ignore_type
            self._save()
        else:
            raise ValueError(f"No entry found for IoCValue: {ioc_value}")

    def delete_entry(self, ioc_value: str):
        """Delete an entry by IoCValue."""
        before = len(self.entries)
        self.entries = [e for e in self.entries if e["IoCValue"] != ioc_value]
        if len(self.entries) == before:
            raise ValueError(f"No entry found to delete for IoCValue: {ioc_value}")
        self._save()

    def insert_bulk(self, entries: List[Dict[str, str]]):
        """Add or replace multiple entries at once."""
        for e in entries:
            self.add_entry(e["IoCType"], e["IoCValue"], e["Direction"], e["IgnoreType"])


class VTAPIKeyManager:
    """
    SDK for managing VirusTotal API key stored in 'vt_api_key' file.
    The file is located in the same directory as this script by default.
    """

    def __init__(self, filename: str = "/etc/slips-sdk/config/vt_api_key"):
        # self.key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        self.key_path = filename

    def set_key(self, api_key: str):
        """Write the API key to the file."""
        with open(self.key_path, "w") as f:
            f.write(api_key.strip())

    def get_key(self) -> str:
        """Read and return the API key from the file."""
        if not os.path.exists(self.key_path):
            raise FileNotFoundError(f"API key file not found: {self.key_path}")
        with open(self.key_path, "r") as f:
            return f.read().strip()

    def delete_key(self):
        """Delete the API key file."""
        if os.path.exists(self.key_path):
            os.remove(self.key_path)

    def key_exists(self) -> bool:
        """Check if the API key file exists."""
        return os.path.isfile(self.key_path)


class SlackBotTokenManager:
    """
    SDK for managing Slack Bot token stored in 'slack_bot_token_secret' file.
    """

    def __init__(self, filename: str = "/etc/slips-sdk/config/slack_bot_token_secret"):
        # self.token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        self.token_path = filename

    def set_token(self, token: str):
        """Write the Slack Bot token to the file."""
        with open(self.token_path, "w") as f:
            f.write(token.strip())

    def get_token(self) -> str:
        """Read and return the Slack Bot token from the file."""
        if not os.path.exists(self.token_path):
            raise FileNotFoundError(f"Slack token file not found: {self.token_path}")
        with open(self.token_path, "r") as f:
            return f.read().strip()

    def delete_token(self):
        """Delete the Slack Bot token file."""
        if os.path.exists(self.token_path):
            os.remove(self.token_path)

    def token_exists(self) -> bool:
        """Check if the token file exists."""
        return os.path.isfile(self.token_path)


class TIFeedManager:
    """
    SDK for managing TI_feeds.csv used by Slips.
    Supports listing, adding, updating, deleting, and saving TI feed entries.
    """

    def __init__(self, filename: str = "/etc/slips-sdk/config/TI_feeds.csv"):
        # self.file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        self.file_path = filename
        self.header_lines: List[str] = []
        self.feeds: List[Dict[str, str]] = []
        self._load()

    def _load(self):
        self.header_lines = []
        self.feeds = []

        with open(self.file_path, "r") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or stripped.startswith(";"):
                    self.header_lines.append(line)
                    continue

                parts = [p.strip() for p in stripped.split(",", 2)]
                if len(parts) == 3:
                    self.feeds.append({
                        "Feed": parts[0],
                        "ThreatLevel": parts[1],
                        "Tags": parts[2]
                    })

    def _save(self):
        with open(self.file_path, "w") as f:
            f.writelines(self.header_lines)
            for feed in self.feeds:
                line = f"{feed['Feed']},{feed['ThreatLevel']},{feed['Tags']}\n"
                f.write(line)

    # ------------------ CRUD Methods ------------------

    def list_feeds(self) -> List[Dict[str, str]]:
        """Return all active feed entries."""
        return self.feeds.copy()

    def find_feed(self, feed_url: str) -> Optional[Dict[str, str]]:
        """Find a feed by its URL."""
        for feed in self.feeds:
            if feed["Feed"] == feed_url:
                return feed
        return None

    def add_feed(self, feed_url: str, threat_level: str, tags: List[str]):
        """Add a new feed or override if it already exists."""
        self.feeds = [f for f in self.feeds if f["Feed"] != feed_url]
        self.feeds.append({
            "Feed": feed_url,
            "ThreatLevel": threat_level,
            "Tags": str(tags)
        })
        self._save()

    def update_feed(self, feed_url: str, threat_level: Optional[str] = None, tags: Optional[List[str]] = None):
        """Update an existing feed's threat level or tags."""
        found = self.find_feed(feed_url)
        if found:
            if threat_level:
                found["ThreatLevel"] = threat_level
            if tags is not None:
                found["Tags"] = str(tags)
            self._save()
        else:
            raise ValueError(f"No feed found for URL: {feed_url}")

    def delete_feed(self, feed_url: str):
        """Delete a feed entry by URL."""
        before = len(self.feeds)
        self.feeds = [f for f in self.feeds if f["Feed"] != feed_url]
        if len(self.feeds) == before:
            raise ValueError(f"No feed found to delete: {feed_url}")
        self._save()

    def insert_bulk(self, entries: List[Dict[str, str]]):
        """Insert or replace multiple feeds at once."""
        for entry in entries:
            self.add_feed(entry["Feed"], entry["ThreatLevel"], eval(entry["Tags"]))


class SSLFeedManager:
    """
    SDK for managing SSL_feeds.csv used by Slips.
    Supports listing, adding, updating, deleting, and saving SSL fingerprint feed entries.
    """

    def __init__(self, filename: str = "/etc/slips-sdk/config/SSL_feeds.csv"):
        # self.file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        self.file_path = filename
        self.header_lines: List[str] = []
        self.feeds: List[Dict[str, str]] = []
        self._load()

    def _load(self):
        self.header_lines = []
        self.feeds = []

        with open(self.file_path, "r") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or stripped.startswith('"URL"'):
                    self.header_lines.append(line)
                    continue

                parts = [p.strip() for p in stripped.split(",", 2)]
                if len(parts) == 3:
                    self.feeds.append({
                        "URL": parts[0],
                        "ThreatLevel": parts[1],
                        "Tags": parts[2]
                    })

    def _save(self):
        with open(self.file_path, "w") as f:
            f.writelines(self.header_lines)
            for feed in self.feeds:
                line = f"{feed['URL']},{feed['ThreatLevel']},{feed['Tags']}\n"
                f.write(line)

    # ------------------ CRUD Methods ------------------

    def list_feeds(self) -> List[Dict[str, str]]:
        """Return all active SSL feed entries."""
        return self.feeds.copy()

    def find_feed(self, url: str) -> Optional[Dict[str, str]]:
        """Find a feed by its URL."""
        for feed in self.feeds:
            if feed["URL"] == url:
                return feed
        return None

    def add_feed(self, url: str, threat_level: str, tags: List[str]):
        """Add or replace an SSL feed entry."""
        self.feeds = [f for f in self.feeds if f["URL"] != url]
        self.feeds.append({
            "URL": url,
            "ThreatLevel": threat_level,
            "Tags": str(tags)
        })
        self._save()

    def update_feed(self, url: str, threat_level: Optional[str] = None, tags: Optional[List[str]] = None):
        """Update an existing SSL feed."""
        found = self.find_feed(url)
        if found:
            if threat_level:
                found["ThreatLevel"] = threat_level
            if tags is not None:
                found["Tags"] = str(tags)
            self._save()
        else:
            raise ValueError(f"No feed found for URL: {url}")

    def delete_feed(self, url: str):
        """Delete a feed by URL."""
        before = len(self.feeds)
        self.feeds = [f for f in self.feeds if f["URL"] != url]
        if len(self.feeds) == before:
            raise ValueError(f"No feed found to delete: {url}")
        self._save()

    def insert_bulk(self, entries: List[Dict[str, str]]):
        """Insert multiple feeds at once."""
        for entry in entries:
            self.add_feed(entry["URL"], entry["ThreatLevel"], eval(entry["Tags"]))


class RiskIQCredentialsManager:
    """
    SDK for managing RiskIQ API credentials stored in 'RiskIQ_credentials' file.
    Format: username:apikey
    """

    def __init__(self, filename: str = "/etc/slips-sdk/config/RiskIQ_credentials"):
        # self.cred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        self.cred_path = filename

    def set_credentials(self, username: str, api_key: str):
        """Store RiskIQ credentials in username:apikey format."""
        with open(self.cred_path, "w") as f:
            f.write(f"{username.strip()}:{api_key.strip()}")

    def get_credentials(self) -> tuple:
        """Retrieve RiskIQ credentials as (username, api_key)."""
        if not os.path.exists(self.cred_path):
            raise FileNotFoundError(f"RiskIQ credentials file not found: {self.cred_path}")
        with open(self.cred_path, "r") as f:
            content = f.read().strip()
            if ":" not in content:
                raise ValueError("Invalid credentials format. Expected username:apikey")
            return tuple(content.split(":", 1))

    def delete_credentials(self):
        """Delete the credentials file."""
        if os.path.exists(self.cred_path):
            os.remove(self.cred_path)

    def credentials_exist(self) -> bool:
        """Check if credentials file exists."""
        return os.path.isfile(self.cred_path)


class JA3FeedManager:
    """
    SDK for managing JA3_feeds.csv used by Slips.
    Supports listing, adding, updating, deleting, and saving JA3 SSL fingerprint feed entries.
    """

    def __init__(self, filename: str = "/etc/slips-sdk/config/JA3_feeds.csv"):
        # self.file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        self.file_path = filename
        self.header_lines: List[str] = []
        self.feeds: List[Dict[str, str]] = []
        self._load()

    def _load(self):
        self.header_lines = []
        self.feeds = []

        with open(self.file_path, "r") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or stripped.startswith('"URL"'):
                    self.header_lines.append(line)
                    continue

                parts = [p.strip() for p in stripped.split(",", 2)]
                if len(parts) == 3:
                    self.feeds.append({
                        "URL": parts[0],
                        "ThreatLevel": parts[1],
                        "Tags": parts[2]
                    })

    def _save(self):
        with open(self.file_path, "w") as f:
            f.writelines(self.header_lines)
            for feed in self.feeds:
                line = f"{feed['URL']},{feed['ThreatLevel']},{feed['Tags']}\n"
                f.write(line)

    # ------------------ CRUD Methods ------------------

    def list_feeds(self) -> List[Dict[str, str]]:
        """Return all JA3 feed entries."""
        return self.feeds.copy()

    def find_feed(self, url: str) -> Optional[Dict[str, str]]:
        """Find a JA3 feed by URL."""
        for feed in self.feeds:
            if feed["URL"] == url:
                return feed
        return None

    def add_feed(self, url: str, threat_level: str, tags: List[str]):
        """Add or replace a JA3 feed."""
        self.feeds = [f for f in self.feeds if f["URL"] != url]
        self.feeds.append({
            "URL": url,
            "ThreatLevel": threat_level,
            "Tags": str(tags)
        })
        self._save()

    def update_feed(self, url: str, threat_level: Optional[str] = None, tags: Optional[List[str]] = None):
        """Update an existing JA3 feed."""
        found = self.find_feed(url)
        if found:
            if threat_level:
                found["ThreatLevel"] = threat_level
            if tags is not None:
                found["Tags"] = str(tags)
            self._save()
        else:
            raise ValueError(f"No feed found for URL: {url}")

    def delete_feed(self, url: str):
        """Delete a JA3 feed by URL."""
        before = len(self.feeds)
        self.feeds = [f for f in self.feeds if f["URL"] != url]
        if len(self.feeds) == before:
            raise ValueError(f"No feed found to delete: {url}")
        self._save()

    def insert_bulk(self, entries: List[Dict[str, str]]):
        """Insert multiple JA3 feeds at once."""
        for entry in entries:
            self.add_feed(entry["URL"], entry["ThreatLevel"], eval(entry["Tags"]))


class LogstashConfigManager:
    """
    SDK for managing a logstash.conf file.
    Supports parsing and updating input, filter, and output blocks (file plugin only).
    """

    def __init__(self, filename: str = "/etc/slips-sdk/config/logstash.conf"):
        # self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        self.config_path = filename
        self._raw_lines = []
        self._load()

    def _load(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"logstash.conf not found: {self.config_path}")
        with open(self.config_path, "r") as f:
            self._raw_lines = f.readlines()

    def _save(self):
        with open(self.config_path, "w") as f:
            f.writelines(self._raw_lines)

    def _update_block(self, block: str, setting: str, value: str):
        """
        Update a setting inside a block ('input', 'output', or 'filter').
        Only supports the 'file' plugin structure.
        """
        inside_block = False
        inside_plugin = False

        for i, line in enumerate(self._raw_lines):
            stripped = line.strip()

            if stripped.startswith(block):
                inside_block = True
            elif inside_block and "{" in stripped:
                inside_plugin = True
            elif inside_block and inside_plugin and setting in stripped:
                # Replace the setting line
                indent = re.match(r'^(\s*)', line).group(1)
                self._raw_lines[i] = f"{indent}{setting} => \"{value}\"\n"
                break
            elif inside_block and stripped == "}":
                inside_plugin = False
                inside_block = False

    # ------------------ Public Setters ------------------

    def set_input_path(self, new_path: str):
        self._update_block("input", "path", new_path)
        self._save()

    def set_input_codec(self, codec: str):
        self._update_block("input", "codec", codec)
        self._save()

    def set_output_path(self, new_path: str):
        self._update_block("output", "path", new_path)
        self._save()

    def set_filter_source(self, field: str):
        self._update_block("filter", "source", field)
        self._save()

    # ------------------ Full Content Access ------------------

    def get_config(self) -> str:
        """Return the full logstash.conf content as a string."""
        return "".join(self._raw_lines)

    def save(self):
        """Save current in-memory content to disk."""
        self._save()


class RedisConfManager:
    """
    SDK for managing a simple redis.conf file (flat key-value pairs).
    Preserves comments and structure.
    """

    def __init__(self, filename: str = "/etc/slips-sdk/config/redis.conf"):
        self.conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        self.conf_path = filename
        self._lines = []
        self._load()

    def _load(self):
        if not os.path.exists(self.conf_path):
            raise FileNotFoundError(f"redis.conf not found: {self.conf_path}")
        with open(self.conf_path, "r") as f:
            self._lines = f.readlines()

    def _save(self):
        with open(self.conf_path, "w") as f:
            f.writelines(self._lines)

    def get(self, key: str) -> str:
        """Get the value of a given key."""
        for line in self._lines:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            if line.startswith(key):
                parts = line.split(None, 1)
                if len(parts) == 2:
                    return parts[1]
        return ""

    def set(self, key: str, value: str):
        """Set or update a configuration value."""
        found = False
        for i, line in enumerate(self._lines):
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                continue
            if stripped.startswith(key):
                self._lines[i] = f"{key} {value}\n"
                found = True
                break
        if not found:
            self._lines.append(f"{key} {value}\n")
        self._save()

    def delete(self, key: str):
        """Remove a key from the config."""
        new_lines = []
        for line in self._lines:
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                new_lines.append(line)
            elif not stripped.startswith(key):
                new_lines.append(line)
        self._lines = new_lines
        self._save()

    def get_all(self) -> dict:
        """Return all key-value pairs as a dictionary."""
        config = {}
        for line in self._lines:
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                continue
            parts = stripped.split(None, 1)
            if len(parts) == 2:
                config[parts[0]] = parts[1]
        return config