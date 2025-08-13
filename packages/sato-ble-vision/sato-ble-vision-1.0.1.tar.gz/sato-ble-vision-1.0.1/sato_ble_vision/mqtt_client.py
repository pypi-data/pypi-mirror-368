import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import pandas as pd
from .api_handler import send_to_resolve_api
from .config import BROKER, PORT, TOPIC, CSV_FILE

mqtt_client = None  # Global variable to store MQTT client
log_callback = None  # Global log function placeholder
logging_enabled = False
printer_print_counts = {}



test_payload = {
    "messageId": "EXTENSION//GK215318/1741608927000",
    "messageType": "extension",
    "messageVersion": "1.5",
    "messageTimestamp": "2025-03-10T12:15:27.000Z",
    "manufacturer": {
        "manufacturerName": "SATO",
        "manufacturerDeviceModel": "PW4NX DT203",
        "manufacturerSerialNumber": "GK215318",
        "manufacturerFamily": "Printer"
    },
    "customer": {
        "customerGuid": "",
        "customerName": "",
        "customerDeviceClass": "Printer",
        "customerSiteId": ""
    },
    "payload": {
        "type": "association-event",
        "lpn": "00002024031812490001",
        "epoch": "1710179496000",
        "categoryId": "gdc-out-pallet",
        "tagQuantity": 1,
        "tagInfo": [
            {
                "tagPayload": "AFFD0200007C2BDE82789BA88F20E2F2B8C6A71694FD47AE1046077B6527F563",
                "tagBdAddress": "0485768B3734",
                "printTimestamp": "2025-03-10T07:15:05.215Z",
                "errors": []
            }
        ]
    }
}


def log(message):
    global log_callback
    if log_callback:
        log_callback(message)
    else:
        print(f"[DEBUG] {message}")


def on_connect(client, userdata, flags, rc):
    from .config import TOPIC
    log(f"[DEBUG] on_connect triggered with rc={rc}")
    if rc == 0:
        log("Connected to MQTT Broker")
        time.sleep(1)
        log(f"Attempting to subscribe to: {TOPIC}")
        time.sleep(1)
        result, mid = client.subscribe(TOPIC, 2)
        log(f"Subscribe result: {result}, MID: {mid}, Topic: {TOPIC}")
        if result != mqtt.MQTT_ERR_SUCCESS:
            log(f"Error subscribing to topic: {TOPIC}")
    else:
        log(f"Failed to connect, return code {rc}")


def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed. MID: {mid}, Granted QoS: {granted_qos}")
    time.sleep(2)
    #client.publish(TOPIC, json.dumps(test_payload), qos=1)
    time.sleep(2)


def on_publish(client, userdata, mid):
    log(f"Message published with MID: {mid}")


def on_message(client, userdata, msg):
    log(f"Message received on topic {msg.topic} with payload: {msg.payload}")

    try:
        msg_data = json.loads(msg.payload.decode())
        msg_details = json.loads(msg.payload.decode())
    except json.JSONDecodeError as e:
        log(f"Error decoding message: {e}")
        return

    message_type = msg_data.get("messageType")
    message_id = msg_data.get("messageId")
    message_timestamp_raw = msg_data.get("messageTimestamp")

    payload = msg_data.get("payload", {})
    lpn_raw = payload.get("lpn", "")
    lpn = lpn_raw.lstrip("0") if lpn_raw else ""

    # Extract printer serial number
    serial_number = msg_data.get("manufacturer", {}).get("manufacturerSerialNumber", "UNKNOWN")

    tag_infos = payload.get("tagInfo", [])

    if not tag_infos:
        if message_type == "errorMessage":
            errors = msg_data.get("errors", [])
            lpn = "ERROR"
            rssi = "N/A"

            valid_error_codes = {"BLE_TAG_READ_ERROR", "BLE_TAG_READ_RSSI_BELOW_THRESHOLD_ERROR"}

            tag_infos = [ {
                "tagPayload": error.get("description") or error.get("message") or error.get("code", "Unknown error"),
                "tagBdAddress": "N/A",
                "printTimestamp": message_timestamp_raw
            } for error in errors if error.get("code") in valid_error_codes ]
        else:
            log("No tagInfo found in the payload.")
            return

    # Count successful prints by serial number
    if message_type != "errorMessage" and tag_infos:
        printer_print_counts[serial_number] = printer_print_counts.get(serial_number, 0) + 1
        log(f"Printer {serial_number} successful print count: {printer_print_counts[serial_number]}")

        # Optional GUI callback
        if hasattr(client, "printer_counter_callback") and callable(client.printer_counter_callback):
            client.printer_counter_callback(serial_number, printer_print_counts[serial_number])

    for tag in tag_infos:
        tag_payload = tag.get("tagPayload", "")
        tag_bd_address = tag.get("tagBdAddress", "")
        print_timestamp_raw = tag.get("printTimestamp", "")

        # RSSI extraction
        hex_rssi = tag_payload[-6:-4]
        try:
            rssi = int(hex_rssi, 16)
            if rssi >= 128:
                rssi -= 256
        except ValueError:
            log(f"Invalid RSSI hex value: {hex_rssi}")
            rssi = None

        log(f"Processed Tag — LPN: {lpn}, Payload: {tag_payload}, BD: {tag_bd_address}, Timestamp: {print_timestamp_raw}, RSSI: {rssi}")

        try:
            message_dt = datetime.strptime(message_timestamp_raw, "%Y-%m-%dT%H:%M:%S.%fZ")
            message_timestamp_unix = int(message_dt.timestamp())
            message_timestamp = message_dt.strftime("%Y-%m-%d %H:%M:%S")

            print_dt = datetime.strptime(print_timestamp_raw, "%Y-%m-%dT%H:%M:%S.%fZ")
            print_timestamp_unix = int(print_dt.timestamp())
            print_timestamp = print_dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            log(f"Error parsing timestamp: {e}")
            continue

        tag_payload_final = tag_payload[:58]  # Trim if needed

        if message_type != "errorMessage":
            resolve_payload = {
                "timestamp": message_timestamp_unix,
                "packets": [{"timestamp": print_timestamp_unix, "payload": tag_payload_final}]
            }
            external_tag_id = send_to_resolve_api(resolve_payload)
        else:
            external_tag_id = "ERROR"

        # Call GUI update for tag data
        if hasattr(client, "tag_callback") and callable(client.tag_callback):
            client.tag_callback(lpn, external_tag_id, tag_payload, tag_bd_address, print_timestamp, rssi, serial_number)

        # CSV Logging
        current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        df = pd.DataFrame([[current_timestamp, message_id, message_timestamp, tag_payload_final,
                            print_timestamp, payload.get("categoryId"), lpn, rssi]],
                          columns=["Timestamp", "Message ID", "Message Timestamp",
                                   "Tag Payload", "Print Timestamp", "Category ID", "LPN", "RSSI"])
        if logging_enabled:
            df.to_csv(CSV_FILE, mode="a", header=False, index=False)
            log(f"Data saved to CSV: {CSV_FILE} for message ID: {message_id}")


def connect_mqtt(log_fn=None, broker=BROKER, port=PORT):
    global mqtt_client, log_callback
    log_callback = log_fn

    log(f"Attempting to connect to MQTT Broker at {broker}:{port}")

    if mqtt_client is None:
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = on_connect
        mqtt_client.on_subscribe = on_subscribe
        mqtt_client.on_publish = on_publish
        mqtt_client.on_message = on_message

        try:
            log("Connecting to broker...")
            mqtt_client.connect(broker, port, 60)
            mqtt_client.loop_start()

            if mqtt_client.is_connected():
                log("MQTT Client connected. Loop started.")

        except Exception as e:
            log(f"Error connecting to MQTT Broker: {e}")
            mqtt_client = None
    else:
        log("MQTT Client is already connected.")



def disconnect_mqtt():
    global mqtt_client
    if mqtt_client:
        log("Disconnecting MQTT client...")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        mqtt_client = None
        log("MQTT Client disconnected successfully.")
    else:
        log("No active MQTT connection to disconnect.")
