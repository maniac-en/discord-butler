# Discord Butler 🤖

A smart auto-updater for Discord on Linux that checks for updates and seamlessly installs them when available. **Now supports first-time Discord installation!**

## How it works

The script will:
1. **Check if Discord is installed** - if not, automatically install it
2. Check your current Discord version
3. Compare with the latest available version
4. If an update is available, download and prompt for sudo password to install
5. Launch Discord

## Requirements

- **Debian/Ubuntu-based Linux system** with `dpkg` package manager
- Python 3.8+
- Python packages: `requests`, `packaging` (see requirements.txt)
- **Polkit authentication agent** - for GUI password prompts (see setup below)

### Setting up Polkit Authentication

Discord Butler uses `pkexec` for secure privilege escalation with GUI authentication dialogs. You need a polkit authentication agent running.

**For i3/dwm/minimal window managers:**
```bash
# Install lightweight polkit agent
sudo apt install lxpolkit

# Add to your window manager startup (e.g., ~/.config/i3/config)
exec --no-startup-id lxpolkit
```

**For other desktop environments:**
```bash
# GNOME-based systems
sudo apt install policykit-1-gnome

# KDE-based systems
sudo apt install polkit-kde-agent-1
```

**Verify setup:**
```bash
# This should show a GUI authentication dialog
pkexec echo "Polkit working!"
```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/maniac-en/discord-butler
   cd discord-butler
   ```

2. Install dependencies (choose one method):

### Method 1: System-level Installation
⚠️ **Note**: Modern pip versions warn against installing packages system-wide. Use this method only if you're comfortable with system-level packages.

```bash
pip install -r requirements.txt --break-system-packages
```

### Method 2: Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Basic Usage

If you installed using a virtual environment, activate it first:
```bash
source venv/bin/activate  # Only needed if using virtual environment
```

Then run the application:
```bash
python main.py
```

### Running from App Launcher

#### For App Launchers (rofi, etc.)

To run Discord Butler from app launchers that support `.desktop` files:

1. Make the script executable:
   ```bash
   chmod +x main.py
   ```

2. Create a desktop entry at `~/.local/share/applications/discord-butler.desktop`:

   **For system-level installation:**
   ```ini
   [Desktop Entry]
   Name=Discord Butler
   Comment=Auto-update Discord and launch
   Exec=/path/to/discord-butler/main.py
   Icon=discord
   Terminal=false
   Type=Application
   Categories=Network;InstantMessaging;
   ```

   **For virtual environment installation:**
   ```ini
   [Desktop Entry]
   Name=Discord Butler
   Comment=Auto-update Discord and launch
   Exec=/path/to/discord-butler/venv/bin/python /path/to/discord-butler/main.py
   Icon=discord
   Terminal=false
   Type=Application
   Categories=Network;InstantMessaging;
   ```

3. Update desktop database:
   ```bash
   update-desktop-database ~/.local/share/applications/
   ```

#### For dmenu

Since dmenu doesn't recognize `.desktop` files, create a wrapper script in your PATH:

> I've provided helper commands to just copy-paste and set it up easily!

⚠️ **WARNING**: Running bash commands from the internet can be dangerous. Always review commands before executing them.

**For system-level installation:**
```bash
# Quick setup (run from the discord-butler directory)
chmod +x main.py && ln -sf "$(pwd)/main.py" ~/.local/bin/discord-butler
```

**For virtual environment installation:**
```bash
# Create a wrapper script
cat > ~/.local/bin/discord-butler << 'EOF'
#!/bin/bash
cd /path/to/discord-butler
source venv/bin/activate
python main.py
EOF

# Make it executable
chmod +x ~/.local/bin/discord-butler
```

**Manual setup**:
1. **System-level**: Create symlink: `ln -sf /full/path/to/discord-butler/main.py ~/.local/bin/discord-butler`
2. **Virtual environment**: Create wrapper script as shown above, replacing `/path/to/discord-butler` with your actual path
3. Ensure `~/.local/bin` is in your PATH (add `export PATH="$HOME/.local/bin:$PATH"` to your shell config if needed)

Now you can run `discord-butler` from dmenu.
