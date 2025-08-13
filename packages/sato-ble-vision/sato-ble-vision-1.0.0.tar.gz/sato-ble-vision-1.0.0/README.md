# SATO BLE Vision

A comprehensive MQTT Broker Control and IoT Data Management Tool designed for SATO BLE tag management and data visualization.

## Features

- **MQTT Broker Management**: Start, stop, and monitor Mosquitto MQTT broker
- **Real-time Data Visualization**: Live display of tag data with filtering and sorting
- **Data Logging**: CSV export of tag events and statistics
- **Multi-preset Configuration**: Support for multiple API configurations
- **Cross-platform**: Works on Windows, macOS, and Linux
- **User-friendly GUI**: Intuitive interface for managing IoT data streams

## Installation

### Prerequisites

1. **Python 3.7 or higher**
2. **Mosquitto MQTT Broker** (external dependency)

#### Installing Mosquitto

**Windows:**
```bash
# Download from https://mosquitto.org/download/
# Or use chocolatey:
choco install mosquitto
```

**macOS:**
```bash
brew install mosquitto
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install mosquitto mosquitto-clients
```

### Installing SATO BLE Vision

```bash
pip install sato-ble-vision
```

## Quick Start

1. **Install the package:**
   ```bash
   pip install sato-ble-vision
   ```

2. **Run the application:**
   ```bash
   sato-ble-vision
   ```

3. **Configure your settings:**
   - The application will create a default configuration file in your home directory
   - Edit `~/.sato_ble_vision/configuration.json` with your API credentials
   - Or use the Settings button in the GUI to configure presets

## Configuration

The application stores configuration in `~/.sato_ble_vision/configuration.json`. You can create multiple presets for different environments.

### Configuration Structure

```json
{
    "last_used": "DEFAULT",
    "DEFAULT": {
        "AuthURL": "https://api.wiliot.com/v1/auth/token/api",
        "ResolveUrl": "https://api.wiliot.com/v1/owner/YOUR_OWNER_ID/resolve",
        "AuthKey": "YOUR_AUTH_KEY_HERE",
        "TOPIC": "eiotpv1/printer/#"
    }
}
```

### Required Fields

- **AuthURL**: Authentication endpoint URL
- **ResolveUrl**: Tag resolution API endpoint
- **AuthKey**: Your API authentication key
- **TOPIC**: MQTT topic to subscribe to

## Usage

### Starting the Application

1. Launch the application using the command line:
   ```bash
   sato-ble-vision
   ```

2. The GUI will open with the main control panel

### Using the Interface

1. **Start Broker**: Click to start the Mosquitto MQTT broker
2. **Connect Client**: Connect to the MQTT broker
3. **Start Logging**: Begin recording tag data to CSV files
4. **View Data**: Switch between different data views:
   - Tag Data: Individual tag events
   - Serial Log: Grouped by serial number
   - General Log: System messages
   - Topic Log: Raw MQTT messages

### Data Views

- **Tag Data**: Shows individual tag events with timestamps, payloads, and RSSI values
- **Serial Log**: Groups tags by serial number with counts
- **General Log**: System messages and broker status
- **Topic Log**: Raw MQTT message data

## File Structure

```
~/.sato_ble_vision/
├── configuration.json    # User configuration
└── logs/                # CSV log files
    ├── mqtt_data_*.csv
    └── mqtt_data_raw_*.csv
```

## API Integration

The application integrates with Wiliot's API for tag resolution and authentication. Configure your API credentials in the settings to enable full functionality.

## Troubleshooting

### Common Issues

1. **Mosquitto not found**: Ensure Mosquitto is installed and in your system PATH
2. **Configuration errors**: Check your API credentials in the configuration file
3. **Permission errors**: Ensure the application has write access to your home directory

### Logs

Log files are stored in `~/.sato_ble_vision/logs/` and include:
- Tag event data
- Raw MQTT messages
- Error logs

## Development

### Building from Source

```bash
git clone <repository-url>
cd sato-ble-vision
pip install -e .
```

### Running Tests

```bash
python -m pytest tests/
```

## License

MIT License - see LICENSE file for details.

## Support

For support and issues, please contact SATO or create an issue in the project repository.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Changelog

### Version 1.0.0
- Initial release
- MQTT broker management
- Real-time data visualization
- CSV logging
- Multi-preset configuration support
 
