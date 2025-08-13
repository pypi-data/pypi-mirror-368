import tkinter as tk
from tkinter import ttk
from .config import (
    get_all_presets, get_preset, save_preset,
    setAuthURL, setResolveURL, setAuthKey,
    setGeneralTopic, setTagTopic, get_last_used_preset, 
    save_config, load_config, update_current_preset
)

def open_settings_window(callback=None):
    settings_root = tk.Toplevel()
    settings_root.title("Settings")
    settings_root.geometry("500x550")

    # Load preset list
    presets = get_all_presets()
    current_preset_name = tk.StringVar(value=get_last_used_preset())
    preset_data = get_preset(current_preset_name.get())

    # StringVars for fields
    auth_var = tk.StringVar(value=preset_data.get("AuthURL", ""))
    resolve_var = tk.StringVar(value=preset_data.get("ResolveUrl", ""))
    ahv_var = tk.StringVar(value=preset_data.get("AuthKey", ""))
    gtopic = tk.StringVar(value="eiotpv1/printer/#")  # Default topic

    def on_preset_change(event):
        preset = get_preset(current_preset_name.get())
        auth_var.set(preset.get("AuthURL", ""))
        resolve_var.set(preset.get("ResolveUrl", ""))
        ahv_var.set(preset.get("AuthKey", ""))
        gtopic.set(preset.get("TOPIC", "eiotpv1/printer/ddata"))

    


    def update_config():
        # Save updated values into the preset
        save_preset(current_preset_name.get(), {
            "AuthURL": auth_var.get(),
            "ResolveUrl": resolve_var.get(),
            "AuthKey": ahv_var.get(),
            "TOPIC": gtopic.get()
        })

        # Update global config state
        setAuthURL(auth_var.get())
        setResolveURL(resolve_var.get())
        setAuthKey(ahv_var.get())
        setGeneralTopic(gtopic.get())

        print(f"Preset '{current_preset_name.get()}' updated.")

        if callback:
            callback(current_preset_name.get())  # <-- Call callback with new preset name
        
        settings_root.destroy()

    def cancel_config():
        print("Cancelled")
        settings_root.destroy()

    def add_preset():
        new_name = new_preset_var.get().strip()
        if not new_name:
            print("Preset name required.")
            return
        if new_name in presets:
            print("Preset already exists.")
            return
        # ✅ Save current values into the new preset
        save_preset(new_name, {
            "AuthURL": auth_var.get(),
            "ResolveUrl": resolve_var.get(),
            "AuthKey": ahv_var.get(),
            "TOPIC": gtopic.get()
        })
        presets.append(new_name)
        preset_combo['values'] = presets
        current_preset_name.set(new_name)

        # No need to reload the fields since they already show the current values
        print(f"Added new preset: {new_name}")



    def delete_preset():
        if len(presets) <= 1:
            print("Can't delete the last remaining preset.")
            return
        preset_to_delete = current_preset_name.get()
        if preset_to_delete not in presets:
            return
        # Remove from config
        config = load_config()
        config.pop(preset_to_delete, None)
        # Update last used
        remaining = [p for p in presets if p != preset_to_delete]
        config["last_used"] = remaining[0]
        save_config(config)

        presets.remove(preset_to_delete)
        preset_combo['values'] = presets
        current_preset_name.set(remaining[0])
        on_preset_change(None)
        print(f"Deleted preset: {preset_to_delete}")

    # === UI Layout ===
    ttk.Label(settings_root, text="Wiliot Resolve Settings:", font=("Arial", 11, "bold")).pack(pady=10)

    ttk.Label(settings_root, text="Preset Configurations").pack()
    preset_combo = ttk.Combobox(settings_root, values=presets, textvariable=current_preset_name, state="readonly")
    preset_combo.pack()
    preset_combo.bind("<<ComboboxSelected>>", on_preset_change)

    ttk.Label(settings_root, text="Wiliot Auth Endpoint:").pack()
    ttk.Entry(settings_root, width=60, textvariable=auth_var).pack()

    ttk.Label(settings_root, text="Wiliot Resolve API Endpoint:").pack()
    ttk.Entry(settings_root, width=60, textvariable=resolve_var).pack()

    ttk.Label(settings_root, text="Wiliot Resolve Key:").pack()
    ttk.Entry(settings_root, width=60, textvariable=ahv_var).pack()

    ttk.Label(settings_root, text="Application Settings:", font=("Arial", 11, "bold")).pack(pady=10)

    ttk.Label(settings_root, text="General Topic Subscription:").pack()
    ttk.Entry(settings_root, width=60, textvariable=gtopic).pack()

    ttk.Separator(settings_root).pack(fill='x', pady=10)

    ttk.Button(settings_root, text="Save", command=update_config).pack(pady=5)
    ttk.Button(settings_root, text="Cancel", command=cancel_config).pack(pady=5)

        # === Add Preset ===
    ttk.Label(settings_root, text="Add New Preset:").pack(pady=(15, 5))
    new_preset_var = tk.StringVar()
    ttk.Entry(settings_root, textvariable=new_preset_var).pack()

   

    ttk.Button(settings_root, text="Add Preset", command=add_preset).pack(pady=5)

    # === Delete Preset ===
    

    ttk.Button(settings_root, text="Delete Selected Preset", command=delete_preset).pack(pady=5)


    settings_root.grab_set()
