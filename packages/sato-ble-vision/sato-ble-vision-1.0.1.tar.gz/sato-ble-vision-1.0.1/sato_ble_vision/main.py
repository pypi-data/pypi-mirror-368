# MIT License
#
#Copyright (c) 2025 SATO
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.



import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import paho.mqtt.client as mqtt
import json
import time
import subprocess
import os
import signal
import threading
from datetime import datetime
import pandas as pd
from .config import BROKER, PORT, TOPIC, CSV_FILE, CSV_FILE_RAW
from .mqtt_client import connect_mqtt, disconnect_mqtt, logging_enabled
from . import settings
from .broker import command



# Global variables
log_file_path = CSV_FILE  
mqtt_client = None  
broker_process = None
tag_counter = 1  
brokerstatus = "Offline"
clientstatus = "Offline"
errorCount = 0

# Logging function 
def log(message, log_text):
    print(message)
    log_text.insert(tk.END, message + '\n')
    log_text.yview(tk.END)
    log_text.update_idletasks()

def browse_log_file():
    global log_file_path
    file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv"), ("All Files", "*.*")])
    if file_path:
        log_file_path = file_path
        log_file_entry.delete(0, tk.END)
        log_file_entry.insert(0, log_file_path)

# --- When a message is received, the mqtt_client.on_message 
# will call its tag_callback (if set) with parameters: lpn, tag_payload, tag_bd_address, print_timestamp.
# This function updates the Treeview.
# Add this global dictionary near your global variables
serial_print_counts = {}  # key: serial number, value: [count, tree_item_id]

def update_table_with_tag_data(lpn, tag_id, tag_payload, tag_bd_address, print_timestamp, rssi, serial_number):
    global tag_counter, logging_enabled, errorCount

    log(f"logging_enabled: {logging_enabled}", log_data_text)

    if tag_payload != "":
        # Always insert into the full Tag Data table
        tag_tree.insert("", "end", values=(tag_counter, print_timestamp, lpn, tag_id, tag_payload, tag_bd_address, rssi))
        tag_tree.yview_moveto(1.0)

        # Error tracking logic
        log(f"LPN is: {lpn}", log_data_text)
        if lpn == "ERROR":
            errorCount += 1
            log(f"ErrorCount is: {errorCount}", log_data_text)
            errorCountvar.set(errorCount)
        else:
            # Update serial number print count ONLY if not an error
            if serial_number in serial_print_counts:
                serial_print_counts[serial_number][0] += 1
                new_count = serial_print_counts[serial_number][0]
                item_id = serial_print_counts[serial_number][1]
                serial_tree.item(item_id, values=(serial_number, new_count))
            else:
                count = 1
                item_id = serial_tree.insert("", "end", values=(serial_number, count))
                serial_print_counts[serial_number] = [count, item_id]
            serial_tree.yview_moveto(1.0)

        # Logging to CSV
        if logging_enabled:
            try:
                df = pd.DataFrame([{
                    "No": tag_counter,
                    "Print Timestamp": print_timestamp,
                    "Association UID": lpn,
                    "Tag ID": tag_id,
                    "Tag Payload": tag_payload,
                    "Tag BD Address": tag_bd_address,
                    "RSSI": rssi
                }])
                if not os.path.exists(log_file_path):
                    df.to_csv(log_file_path, mode='w', index=False)
                else:
                    df.to_csv(log_file_path, mode='a', index=False, header=False)
            except Exception as e:
                log(f"Failed to write to CSV: {e}", log_data_text)

        # Always increment the total tag counter
        tag_counter += 1
        tagCountvar.set(tag_counter - 1)
        successful_read_var.set(tag_counter - errorCount - 1)

# --- The on_message function in mqtt_client.py remains unchanged, and it calls:
#    if hasattr(client, "tag_callback") and callable(client.tag_callback):
#         client.tag_callback(lpn, tag_payload, tag_bd_address, print_timestamp)

def start_broker():
    global broker_process
    if broker_process:
        log("Broker already running!", log_data_text)
        return
    log("Starting Mosquitto MQTT Broker...", log_data_text)
    def run_broker():
        global broker_process
        try:
            # Try to find mosquitto.conf in common locations
            mosquitto_conf_paths = [
                "C:\\Program Files\\mosquitto\\mosquitto.conf",
                "/etc/mosquitto/mosquitto.conf",
                "/usr/local/etc/mosquitto/mosquitto.conf",
                "mosquitto.conf"
            ]
            
            mosquitto_conf = None
            for path in mosquitto_conf_paths:
                if os.path.exists(path):
                    mosquitto_conf = path
                    break
            
            if mosquitto_conf:
                mosquitto_cmd = ["mosquitto", "-v", "-c", mosquitto_conf]
            else:
                mosquitto_cmd = ["mosquitto", "-v"]
            broker_process = subprocess.Popen(
                mosquitto_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            log("Mosquitto Broker started successfully.", log_data_text)
            global brokerstatus     
            brokerstatus = "Online"
            stop_button.config(state="normal")
            start_button.config(state="disabled")
            settings_button.config(state="disabled")
            broker_status_status.config(text=brokerstatus)
            def read_output(pipe, log_text_widget):
                for line in iter(pipe.readline, ''):
                    log(line.strip(), log_text_widget)
                pipe.close()
            threading.Thread(target=read_output, args=(broker_process.stdout, log_text), daemon=True).start()
            threading.Thread(target=read_output, args=(broker_process.stderr, log_text), daemon=True).start()
        except Exception as e:
            log(f"Error starting Mosquitto Broker: {e}", log_data_text)
    threading.Thread(target=run_broker, daemon=True).start()

def connect_client():
    try:
        # Refresh settings values
        from .config import BROKER, PORT, TOPIC  # or use importlib.reload if config is dynamic
        from . import mqtt_client
        mqtt_client.connect_mqtt(lambda message: log(message, log_data_text), broker=BROKER, port=PORT)

        global clientstatus
        clientstatus = "Online"
        disconnect_button.config(state="normal")
        connect_button.config(state="disabled")
        client_status_status.config(text=clientstatus)

        mqtt_client.mqtt_client.tag_callback = update_table_with_tag_data
    except Exception as e:
        log(str(e), log_data_text)

def disconnect_client():
    disconnect_mqtt()
    clientstatus = "Offline"
    connect_button.config(state="normal")
    disconnect_button.config(state="disabled")
    client_status_status.config(text=clientstatus)

def stop_broker():
    global mqtt_client, broker_process
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        mqtt_client = None
        log("MQTT Client stopped.", log_data_text)
        global clientstatus
        clientstatus = "Offline"
        client_status_status.config(text=clientstatus)
    if broker_process:
        log("Stopping MQTT Broker...", log_data_text)
        broker_process.terminate()
        broker_process.wait()
        broker_process = None
        log("Broker stopped.", log_data_text)
        global brokerstatus
        brokerstatus = "Offline"
        start_button.config(state="normal")
        stop_button.config(state="disabled")
        settings_button.config(state="normal")
        broker_status_status.config(text=brokerstatus)
    else:
        log("No active broker to stop.", log_data_text)

def on_closing():
    stop_broker()
    log("Closing application...", log_data_text)
    root.quit()
    root.destroy()

def show_data_log():
    log_text.grid_remove()
    scrollbar.grid_remove()
    tag_tree.grid_remove()
    serial_tree.grid_remove()
    serial_scrollbar.grid_remove()
    log_data_text.grid()
    scrollbar_data.grid()
    

def show_tag_log():
    log_text.grid_remove()
    scrollbar.grid_remove()
    log_data_text.grid_remove()
    scrollbar_data.grid_remove()
    serial_tree.grid_remove()
    serial_scrollbar.grid_remove()
    tag_tree.grid()
    tag_scrollbar.grid()
    

def show_general_log():
    log_data_text.grid_remove()
    scrollbar_data.grid_remove()
    tag_tree.grid_remove()
    log_text.grid()
    scrollbar.grid()
    serial_tree.grid_remove()
    serial_scrollbar.grid_remove()


def show_serial():
    log_text.grid_remove()
    scrollbar.grid_remove()
    log_data_text.grid_remove()
    scrollbar_data.grid_remove()
    tag_tree.grid_remove()
    tag_scrollbar.grid_remove()
    serial_tree.grid()
    serial_scrollbar.grid()

#def show_serial():
 #   serial_tree.lift()

#def show_tag_log():
 #   tag_tree.lift()

#def show_general_log():
 #   log_text.lift()

#def show_data_log():
 #   log_data_text.lift()

def start_logging():
    global logging_enabled
    logging_enabled = True
    log_stop_button.config(state="normal")
    log_start_button.config(state="disabled")
    log("Logging started.", log_data_text)

def stop_logging():
    global logging_enabled
    logging_enabled = False
    log_start_button.config(state="normal")
    log_stop_button.config(state="disabled")
    log("Logging stopped.", log_data_text)

def clear_tag_data():
    global tag_counter
    global errorCount
    for item in tag_tree.get_children():
        tag_tree.delete(item)
    for item in serial_tree.get_children():
        serial_tree.delete(item)
    serial_print_counts.clear()
    tag_counter = 1
    errorCount = 0
    errorCountvar.set(0)
    tagCountvar.set(0)
    successful_read_var.set(0)


def open_settings():
    settings.open_settings_window(callback=on_settings_saved)

def on_settings_saved(new_preset_name):
    global current_preset_
    current_preset_.set(new_preset_name)

def main():
    """Main entry point for the application"""
    global root, log_file_path, mqtt_client, broker_process, tag_counter, brokerstatus, clientstatus, errorCount
    global log_text, log_data_text, tag_tree, serial_tree, errorCountvar, tagCountvar, successful_read_var
    global start_button, connect_button, disconnect_button, stop_button, settings_button
    global broker_status_status, client_status_status, current_preset_
    global log_file_entry, log_start_button, log_stop_button, clear_button
    global show_log_tag, show_topic_log, show_log, show_serial_log




# --- GUI Setup ---
root = tk.Tk()
root.title("MQTT Broker Control")
root.geometry("1400x700")
root.protocol("WM_DELETE_WINDOW", on_closing)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3)

frame_left = ttk.Frame(root, relief="groove", borderwidth=4)
frame_left.grid(row=0, column=0, rowspan=2, columnspan=2, padx=5, pady=5, sticky="nsew")
frame_right = ttk.Frame(root, relief="groove", borderwidth=4)
frame_right.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky="nsew")
frame_log = ttk.Frame(root, relief="groove", borderwidth=4)
frame_log.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
frame_log.grid_rowconfigure(0, weight=1)
frame_log.grid_columnconfigure(0, weight=1)
frame_bottom = ttk.Frame(root, relief="groove", borderwidth=4)
frame_bottom.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")


script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, "pics", "logo_b.png")
icon_path = os.path.join(script_dir,"pics", "mqtt.png")
settings_path = os.path.join(script_dir,"pics", "settingsv3.png")

logo = tk.PhotoImage(file=logo_path)
logo_label = ttk.Label(root, image=logo)
logo_label.image = logo 
logo_label.grid(row=0, column=2, pady=10, padx=10, sticky="ne")

icon_img = tk.PhotoImage(file=icon_path)
root.iconphoto(True, icon_img)

settings_img = tk.PhotoImage(file=settings_path)

errorCountvar = tk.IntVar(value=0)
tagCountvar = tk.IntVar(value=0)
successful_read_var = tk.IntVar(value=0)

# Left section title
left_title_label = ttk.Label(frame_left, text="MQTT Broker/Client Controls", font=("Arial", 12, "bold"))
left_title_label.grid(row=0, column=0, columnspan=2, padx=5, pady=10, sticky="w")

# Right section title
right_title_label = ttk.Label(frame_right, text="Log File Controls", font=("Arial", 12, "bold"))
right_title_label.grid(row=0, column=0, columnspan=3, padx=5, pady=10, sticky="w")

start_button = ttk.Button(frame_left, text="Start Broker", width=15, command=start_broker)
start_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
connect_button = ttk.Button(frame_left, text="Connect Client",width=15, command=connect_client)
connect_button.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
disconnect_button = ttk.Button(frame_left, text="Disconnect Client",width=16, state="disabled", command=disconnect_client)
disconnect_button.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
stop_button = ttk.Button(frame_left, text="Stop Broker",width=15, state="disabled", command=stop_broker)
stop_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

broker_ip_label = ttk.Label(frame_left, text="Broker IP Address:")
broker_ip_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
broker_ip_value = ttk.Label(frame_left, text=BROKER)
broker_ip_value.grid(row=2, column=1, padx=5, pady=5, sticky="w")
subscribe_label = ttk.Label(frame_left, text="Current Configuration:")
subscribe_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

current_preset_ = tk.StringVar(value=settings.get_last_used_preset())

subscribe_entry = ttk.Label(frame_left, textvariable=current_preset_)
subscribe_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

broker_status_label = ttk.Label(frame_left, text="Broker Status:")
broker_status_label.grid(row=2,column=2,padx=5, pady=5, sticky="w")
client_status_label = ttk.Label(frame_left, text="Client Status:")
client_status_label.grid(row=3,column=2,padx=5, pady=5, sticky="w")

broker_status_status = ttk.Label(frame_left, text=brokerstatus)
broker_status_status.grid(row=2,column=3,padx=5, pady=5, sticky="w")

client_status_status = ttk.Label(frame_left, text=clientstatus)
client_status_status.grid(row=3,column=3,padx=5, pady=5, sticky="w")

error_count_label = ttk.Label(frame_bottom, text="Error Count:")
error_count_label.grid(row=3, column=3,padx=5,pady=5,sticky="" )

error_count = ttk.Label(frame_bottom, textvariable=errorCountvar)
error_count.grid(row=3, column=4, padx=5,pady=5,sticky="" )

tag_count_label = ttk.Label(frame_bottom, text="Total Tag Count:")
tag_count_label.grid(row=3, column=5,padx=5,pady=5,sticky="" )

tag_count = ttk.Label(frame_bottom, textvariable=tagCountvar)
tag_count.grid(row=3, column=6, padx=5,pady=5,sticky="" )

successful_read_count_label = ttk.Label(frame_bottom, text="Successful Reads:")
successful_read_count_label.grid(row=3, column=1,padx=5,pady=5,sticky="" )

successful_read_count = ttk.Label(frame_bottom, textvariable=successful_read_var)
successful_read_count.grid(row=3, column=2, padx=5,pady=5,sticky="" )

settings_button = ttk.Button(frame_left, image=settings_img, command=open_settings)
settings_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

log_file_label = ttk.Label(frame_right, text="Log File:")
log_file_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
log_file_entry = ttk.Entry(frame_right, width=30)
log_file_entry.insert(0, log_file_path)
log_file_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
log_start_button = ttk.Button(frame_right, width=15, text="Start Logging",command=start_logging)
log_start_button.grid(row=2, column=0, padx=10, pady=5, sticky="e")
log_stop_button = ttk.Button(frame_right, width=15, text="Stop Logging", state="disabled",command=stop_logging)
log_stop_button.grid(row=2, column=1, padx=10, pady=5, sticky="w")
browse_button = ttk.Button(frame_right, text="Browse",width=10, command=browse_log_file)
browse_button.grid(row=1, column=2, padx=5, pady=5, sticky="w")

clear_button = ttk.Button(frame_right, text="Clear Tags",width=15, command=clear_tag_data)
clear_button.grid(row=3, column=0, padx=10, pady=5, sticky="e")

# Text widget for general logs (hidden by default)
log_text = tk.Text(frame_log, height=10, wrap=tk.WORD)
log_text.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
log_text.grid_remove()

# Text widget for detailed data logs (visible by default)
log_data_text = tk.Text(frame_log, height=10, wrap=tk.WORD)
log_data_text.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
log_data_text.grid_remove()

# Text Widget for Serial Grouping
#show_serial_data = ttk.Button(frame_right, text="Show Serial Data", command=show_serial)
#show_serial_data.grid(row=3, column=5, padx=5, pady=5, sticky="sw")

# --- Create a Treeview widget for tag data ---
from tkinter import ttk
tag_tree = ttk.Treeview(frame_log, columns=("No", "Print Timestamp", "Printjob UID", "Tag ID", "Tag Payload", "Tag BD Address", "RSSI"), show="headings")
tag_tree.heading("No", text="No")
tag_tree.heading("Print Timestamp", text="Print Timestamp")
tag_tree.heading("Printjob UID", text="Association UID")
tag_tree.heading("Tag ID", text="Tag ID")
tag_tree.heading("Tag Payload", text="Tag Payload")
tag_tree.heading("Tag BD Address", text="Tag BD Address")
tag_tree.heading("RSSI", text="RSSI")
tag_tree.column("No", width=10, anchor="center")
tag_tree.column("Print Timestamp", width=100, anchor="center")
tag_tree.column("Printjob UID", width=100, anchor="center") 
tag_tree.column("Tag ID", width=100, anchor="center")
tag_tree.column("Tag Payload", width=100, anchor="w")
tag_tree.column("Tag BD Address", width=100, anchor="center")
tag_tree.column("RSSI", width=100, anchor="center")
tag_tree.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)


# --- New Treeview for Serial Numbers and Counters ---
serial_tree = ttk.Treeview(frame_log, columns=( "Serial Number", "No"), show="headings")
serial_tree.heading("Serial Number", text="Serial Number")
serial_tree.heading("No", text="No")
serial_tree.column("Serial Number", width=200, anchor="center")
serial_tree.column("No", width=40, anchor="center")
serial_tree.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
serial_tree.grid_remove()  # Hide initially

# Scrollbar for serial_tree
serial_scrollbar = ttk.Scrollbar(frame_log, command=serial_tree.yview)
serial_scrollbar.grid(row=0, column=4, sticky="ns")
serial_tree.config(yscrollcommand=serial_scrollbar.set)
serial_scrollbar.grid_remove()



# Scrollbars for text widgets and Treeview
scrollbar = ttk.Scrollbar(frame_log, command=log_text.yview)
scrollbar.grid(row=0, column=4, sticky="ns")
log_text.config(yscrollcommand=scrollbar.set)
scrollbar.grid_remove()


scrollbar_data = ttk.Scrollbar(frame_log, command=log_data_text.yview)
scrollbar_data.grid(row=0, column=4, sticky="ns")
log_data_text.config(yscrollcommand=scrollbar_data.set)
scrollbar_data.grid_remove()

tag_scrollbar = ttk.Scrollbar(frame_log, command=tag_tree.yview)
tag_scrollbar.grid(row=0, column=4, sticky="ns")
tag_tree.config(yscrollcommand=tag_scrollbar.set)

show_log_tag = ttk.Button(frame_right, text="Show Tag Data", command=lambda: [log_text.grid_remove(),
                                                                              log_data_text.grid_remove(),
                                                                              serial_tree.grid_remove(),
                                                                              serial_scrollbar.grid_remove(),
                                                                              tag_tree.grid(),
                                                                              tag_scrollbar.grid()])
show_log_tag.grid(row=3, column=4, padx=5, pady=5, sticky="sw")
show_topic_log = ttk.Button(frame_right, text="Show Topic Log", command=lambda: [tag_tree.grid_remove(),
                                                                                 tag_scrollbar.grid_remove(),
                                                                                 log_text.grid_remove(),
                                                                                 serial_tree.grid_remove(),
                                                                                 serial_scrollbar.grid_remove(),
                                                                                 log_data_text.grid(),
                                                                                 scrollbar_data.grid()])
show_topic_log.grid(row=3, column=2, padx=5, pady=5, sticky="sw")
show_log = ttk.Button(frame_right, text="Show General Log", command=lambda: [tag_tree.grid_remove(),
                                                                             tag_scrollbar.grid_remove(),
                                                                             log_data_text.grid_remove(),
                                                                             serial_tree.grid_remove(),
                                                                             serial_scrollbar.grid_remove(),
                                                                             log_text.grid(),
                                                                             scrollbar.grid()])

show_serial_log = ttk.Button(frame_right, text="Show Serial Log", command=lambda: [log_text.grid_remove(),
                                                                                   log_data_text.grid_remove(),
                                                                                   tag_tree.grid_remove(),
                                                                                   tag_scrollbar.grid_remove(),
                                                                                   serial_tree.grid(),
                                                                                   serial_scrollbar.grid()])
show_serial_log.grid(row=3, column=6, padx=5, pady=5, sticky="sw")

show_log.grid(row=3, column=3, padx=5, pady=5, sticky="sw")

root.mainloop()

if __name__ == "__main__":
    main()