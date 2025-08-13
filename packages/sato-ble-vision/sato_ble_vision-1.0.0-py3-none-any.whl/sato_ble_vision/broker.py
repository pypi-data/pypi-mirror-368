import subprocess
import sys
import time
import os
import signal

# Try to find mosquitto.conf in common locations
def get_mosquitto_config_path():
    config_paths = [
        "C:\\Program Files\\mosquitto\\mosquitto.conf",
        "/etc/mosquitto/mosquitto.conf",
        "/usr/local/etc/mosquitto/mosquitto.conf",
        "mosquitto.conf"
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            return path
    return None

MOSQUITTO_CONFIG_PATH = get_mosquitto_config_path() 

# Build the command
command = ["mosquitto", "-v"]
if MOSQUITTO_CONFIG_PATH:
    command = ["mosquitto", "-c", MOSQUITTO_CONFIG_PATH]
def start_mosquitto():
    try:
        print("Starting Mosquitto broker...")
        sys.stdout.flush()

        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        return process

    except Exception as e:
        print(f"Failed to start Mosquitto: {e}")
        sys.stdout.flush()
        return None


def stop_mosquitto(process):
    print("\nStopping Mosquitto broker...")
    if process:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    print("Mosquitto broker stopped.")

if __name__ == "__main__":
    process = start_mosquitto()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_mosquitto(process)
