from slips.config import (
    IDSConfig,
    IrisConfig,
    WardenConfig, 
    WhitelistConfig, 
    VTAPIKeyManager, 
    SlackBotTokenManager, 
    TIFeedManager, 
    SSLFeedManager, 
    RiskIQCredentialsManager,
    JA3FeedManager,
    LogstashConfigManager,
    RedisConfManager
)


slieps_config = IDSConfig()

print(slieps_config.get_all_config())
print("*"*10)

config = IrisConfig()
print(config.get_all_config())  


conf = WardenConfig()

print(conf.get_url())

conf = WhitelistConfig()

# List all entries
for e in conf.list_whitelist():
    print(e)


key_mgr = VTAPIKeyManager()

# Set key
key_mgr.set_key("your-virustotal-api-key")

# Get key
print("API Key:", key_mgr.get_key())

# Check if exists
if key_mgr.key_exists():
    print("Key file is present.")

# Delete key
# key_mgr.delete_key()


token_mgr = SlackBotTokenManager()

# Save token
token_mgr.set_token("xoxb-your-slack-bot-token")

# Retrieve token
print("Slack Token:", token_mgr.get_token())

# Check existence
if token_mgr.token_exists():
    print("Slack token is stored.")

# Delete token
# token_mgr.delete_token()


ti = TIFeedManager()

# List all feeds
for f in ti.list_feeds():
    print(f)


print("============================================= SSL MNG FEED +++++__________________________--")

ssl_mgr = SSLFeedManager()

# List all SSL feeds
for f in ssl_mgr.list_feeds():
    print(f)

print("============================================= RISK IQ MNG FEED +++++__________________________--")

creds = RiskIQCredentialsManager()

# Save credentials
creds.set_credentials("your_email@example.com", "your_riskiq_api_key")

# Retrieve credentials
username, api_key = creds.get_credentials()
print("Username:", username)
print("API Key:", api_key)

# Check if file exists
if creds.credentials_exist():
    print("Credentials file exists.")

# Delete credentials
# creds.delete_credentials()


ja3_mgr = JA3FeedManager()

# List all JA3 feeds
print(ja3_mgr.list_feeds())

# Add a feed
ja3_mgr.add_feed("https://example.com/ja3.csv", "high", ["malicious", "ssl"])

# Update it
ja3_mgr.update_feed("https://example.com/ja3.csv", threat_level="critical")

# Delete it
ja3_mgr.delete_feed("https://example.com/ja3.csv")

# Bulk insert
ja3_mgr.insert_bulk([
    {"URL": "https://one.com/ja3.csv", "ThreatLevel": "low", "Tags": "['phishing']"},
    {"URL": "https://two.com/ja3.csv", "ThreatLevel": "medium", "Tags": "['c2']"}
])


config = LogstashConfigManager()

# Update input path
config.set_input_path("/var/log/slips/alerts.json")

# Update codec
config.set_input_codec("json")

# Update filter source
config.set_filter_source("message")

# Update output path
config.set_output_path("/var/log/processed/output.txt")

# Print full config
print(config.get_config())


conf = RedisConfManager()

print("daemonize:", conf.get("daemonize"))
conf.set("save", "900 1")
conf.set("appendonly", "yes")
conf.delete("stop-writes-on-bgsave-error")

print(conf.get_all())
