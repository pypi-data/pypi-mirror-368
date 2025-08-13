import json
import os
import socket
import psutil
import time
from pathlib import Path

# Get user's home directory for configuration storage
USER_HOME = Path.home()
CONFIG_DIR = USER_HOME / ".sato_ble_vision"
CONFIG_FILE = CONFIG_DIR / "configuration.json"
LOGS_DIR = CONFIG_DIR / "logs"
DEFAULT_PRESET = "DEFAULT"

# Ensure directories exist
CONFIG_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# === Configuration Manager ===

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}  # File is empty
                return json.loads(content)
        except json.JSONDecodeError:
            print("Warning: configuration.json contains invalid JSON. Using blank config.")
            return {}
    else:
        # Create default configuration from template
        create_default_config()
        return load_config()
    return {}


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def create_default_config():
    """Create a default configuration file from template"""
    import pkg_resources
    
    try:
        # Try to get template from package
        template_path = pkg_resources.resource_filename('sato_ble_vision', 'templates/configuration_template.json')
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                template_data = json.load(f)
        else:
            # Fallback template
            template_data = {
                "last_used": "DEFAULT",
                "DEFAULT": {
                    "AuthURL": "https://api.wiliot.com/v1/auth/token/api",
                    "ResolveUrl": "https://api.wiliot.com/v1/owner/YOUR_OWNER_ID/resolve",
                    "AuthKey": "YOUR_AUTH_KEY_HERE",
                    "TOPIC": "eiotpv1/printer/#"
                }
            }
        
        save_config(template_data)
        print(f"Created default configuration at: {CONFIG_FILE}")
        print("Please edit the configuration file with your API credentials.")
        
    except Exception as e:
        print(f"Error creating default config: {e}")
        # Create minimal config
        minimal_config = {
            "last_used": "DEFAULT",
            "DEFAULT": {
                "AuthURL": "",
                "ResolveUrl": "",
                "AuthKey": "",
                "TOPIC": "eiotpv1/printer/#"
            }
        }
        save_config(minimal_config)

def get_all_presets():
    config = load_config()
    return [k for k in config.keys() if k != "last_used"]

def get_preset(name):
    config = load_config()
    return config.get(name, {})

def save_preset(name, preset_data):
    config = load_config()
    config[name] = preset_data
    config["last_used"] = name  # ✅ Persist selected preset
    save_config(config)

def get_last_used_preset():
    config = load_config()
    presets = get_all_presets()
    return config.get("last_used", presets[0] if presets else DEFAULT_PRESET)

# === Load default preset on startup ===
default_preset = get_preset(get_last_used_preset())

AUTH_URL = default_preset.get("AuthURL", "")
RESOLVE_URL = default_preset.get("ResolveUrl", "")
AUTHORIZATION_HEADER_VALUE = default_preset.get("AuthKey", "")
TOPIC = default_preset.get("TOPIC", "")

# === Setters ===
def setResolveURL(data): global RESOLVE_URL; RESOLVE_URL = data
def setAuthURL(data): global AUTH_URL; AUTH_URL = data
def setAuthKey(data): global AUTHORIZATION_HEADER_VALUE; AUTHORIZATION_HEADER_VALUE = data
def setGeneralTopic(data): global TOPIC; TOPIC = data
def setTagTopic(data): global TOPIC; TOPIC = data

# === IP Utilities ===
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

def get_wifi_ip():
    try:
        preferred = ["wifi", "wi-fi", "wlan"]
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for name, addrs in interfaces.items():
            if not any(k in name.lower() for k in preferred): continue
            if not stats[name].isup: continue
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("169.254."):
                    return addr.address
        return None
    except:
        return None

def get_ip_from_network_interface():
    try:
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for name, addrs in interfaces.items():
            if not stats[name].isup: continue
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("169.254."):
                    return addr.address
        return None
    except:
        return None

def get_best_local_ip():
    for method in [get_wifi_ip, get_ip_from_network_interface, get_local_ip]:
        ip = method()
        if ip and ip != "localhost":
            return ip
    return "localhost"

def update_current_preset(auth_url, resolve_url, auth_key, topic):
    current_name = get_last_used_preset()
    config = load_config()
    config[current_name] = {
        "AuthURL": auth_url,
        "ResolveUrl": resolve_url,
        "AuthKey": auth_key,
        "TOPIC": topic
    }
    config["last_used"] = current_name
    save_config(config)


# === Logging ===
def create_log_name(): return str(LOGS_DIR / f"mqtt_data_{int(time.time())}.csv")
def create_log_name_raw(): return str(LOGS_DIR / f"mqtt_data_raw_{int(time.time())}.csv")

BROKER = get_best_local_ip()
PORT = 1883
CSV_FILE = create_log_name()
CSV_FILE_RAW = create_log_name_raw()

# === Debug ===
print(f"MQTT Broker: {BROKER}")
print(f"Auth URL: {AUTH_URL}")
print(f"Resolve URL: {RESOLVE_URL}")
