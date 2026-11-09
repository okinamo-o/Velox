#!/usr/bin/env bash
# ==============================================================================
# ⚡ VELOX BROWSER - Linux Quick-Start, Auto-Updater & Build Helper
# https://github.com/okinamo-o/Velox
# ==============================================================================
set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}====================================================${NC}"
echo -e "${CYAN}          ⚡ VELOX BROWSER FOR LINUX               ${NC}"
echo -e "${CYAN}====================================================${NC}"

show_menu() {
    echo -e "Please select an option:"
    echo -e "  ${GREEN}1)${NC} Install / Update Velox via Wine / Proton (Instant, No Compile Required)"
    echo -e "  ${GREEN}2)${NC} Check & Apply Latest Velox Update In-Place (Preserves Tabs & Profile)"
    echo -e "  ${GREEN}3)${NC} Build Native Linux Velox from Source (Requires ~80GB & C++ tools)"
    echo -e "  ${GREEN}4)${NC} Create Desktop Launcher (.desktop) for Velox"
    echo -e "  ${GREEN}5)${NC} Exit"
    echo ""
    read -rp "Enter choice [1-5]: " choice
    case "$choice" in
        1) install_wine_runner ;;
        2) update_velox_linux ;;
        3) build_native_linux ;;
        4) create_desktop_entry ;;
        5) exit 0 ;;
        *) echo -e "${RED}Invalid option.${NC}"; exit 1 ;;
    esac
}

install_wine_runner() {
    echo -e "\n${YELLOW}[*] Checking for Wine / Bottles...${NC}"
    if ! command -v wine &> /dev/null; then
        echo -e "${RED}[!] Wine is not installed.${NC}"
        echo "Please install wine first:"
        echo "  Ubuntu/Debian/Zorin OS: sudo apt update && sudo apt install -y wine curl unzip"
        echo "  Arch Linux:             sudo pacman -S wine curl unzip"
        echo "  Fedora:                 sudo dnf install wine curl unzip"
        exit 1
    fi

    INSTALL_DIR="$HOME/.local/share/velox"
    mkdir -p "$INSTALL_DIR"

    echo -e "${GREEN}[*] Fetching latest Velox release info from GitHub...${NC}"
    LATEST_JSON=$(curl -fsSL "https://raw.githubusercontent.com/okinamo-o/Velox/main/dist/version.json?t=$(date +%s)")
    DOWNLOAD_URL=$(echo "$LATEST_JSON" | grep -o 'https://[^"]*Portable-x64.zip' | head -n 1)
    VERSION=$(echo "$LATEST_JSON" | grep -o '"version": *"[^"]*"' | head -n 1 | cut -d '"' -f 4)

    if [ -z "$DOWNLOAD_URL" ]; then
        DOWNLOAD_URL="https://github.com/okinamo-o/Velox/releases/latest/download/VeloxSetup.exe"
        echo -e "${YELLOW}[*] Downloading Velox installer...${NC}"
        curl -fL "$DOWNLOAD_URL" -o "$INSTALL_DIR/VeloxSetup.exe"
        echo -e "${GREEN}[*] Launching installer with Wine...${NC}"
        wine "$INSTALL_DIR/VeloxSetup.exe"
    else
        echo -e "${GREEN}[*] Downloading Velox v$VERSION Portable...${NC}"
        curl -fL "$DOWNLOAD_URL" -o "$INSTALL_DIR/velox-portable.zip"
        echo -e "${GREEN}[*] Extracting Velox v$VERSION...${NC}"
        unzip -q -o "$INSTALL_DIR/velox-portable.zip" -d "$INSTALL_DIR"
        rm -f "$INSTALL_DIR/velox-portable.zip"
        echo "$VERSION" > "$INSTALL_DIR/VERSION"

        # Create runner script that also syncs any staged in-app updates
        cat << 'EOF' > "$INSTALL_DIR/velox"
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export WINEPREFIX="$HOME/.local/share/velox/wineprefix"
APP_DIR="$WINEPREFIX/drive_c/users/$USER/AppData/Local/Velox/Application"
if [ -d "$APP_DIR" ] && [ -f "$APP_DIR/chrome.exe" ]; then
    exec wine "$APP_DIR/chrome.exe" "$@"
elif [ -f "$SCRIPT_DIR/velox.exe" ]; then
    exec wine "$SCRIPT_DIR/velox.exe" "$@"
else
    exec wine "$SCRIPT_DIR/chrome.exe" "$@"
fi
EOF
        chmod +x "$INSTALL_DIR/velox"
        
        # Link to ~/.local/bin
        mkdir -p "$HOME/.local/bin"
        ln -sf "$INSTALL_DIR/velox" "$HOME/.local/bin/velox"

        create_desktop_entry
        echo -e "\n${GREEN}[✓] Velox v$VERSION installed successfully! Launch it with 'velox' or from your application menu.${NC}"
    fi
}

update_velox_linux() {
    INSTALL_DIR="$HOME/.local/share/velox"
    mkdir -p "$INSTALL_DIR"
    LOCAL_VER="none"
    if [ -f "$INSTALL_DIR/VERSION" ]; then
        LOCAL_VER=$(cat "$INSTALL_DIR/VERSION" | tr -d '[:space:]')
    fi

    echo -e "${GREEN}[*] Checking GitHub for Velox updates (Installed: $LOCAL_VER)...${NC}"
    LATEST_JSON=$(curl -fsSL "https://raw.githubusercontent.com/okinamo-o/Velox/main/dist/version.json?t=$(date +%s)")
    VERSION=$(echo "$LATEST_JSON" | grep -o '"version": *"[^"]*"' | head -n 1 | cut -d '"' -f 4)
    echo -e "${CYAN}[*] Latest Remote Version: v$VERSION${NC}"

    install_wine_runner
}

create_desktop_entry() {
    DESKTOP_DIR="$HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"

    # Download icon if available
    ICON_PATH="$HOME/.local/share/velox/velox.png"
    if [ ! -f "$ICON_PATH" ]; then
        curl -sSL "https://raw.githubusercontent.com/okinamo-o/Velox/main/branding/assets/velox_logo_512.png" -o "$ICON_PATH" 2>/dev/null || true
    fi

    cat << EOF > "$DESKTOP_DIR/velox.desktop"
[Desktop Entry]
Name=Velox Browser
Comment=The Ultra-Fast, Shielded Web Browser
Exec=$HOME/.local/bin/velox %U
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;x-scheme-handler/http;x-scheme-handler/https;
StartupWMClass=velox.exe
EOF

    chmod +x "$DESKTOP_DIR/velox.desktop"
    echo -e "${GREEN}[✓] Desktop entry created at $DESKTOP_DIR/velox.desktop${NC}"
}

build_native_linux() {
    echo -e "\n${CYAN}====================================================${NC}"
    echo -e "${CYAN}     NATIVE LINUX BUILD FROM SOURCE GUIDE          ${NC}"
    echo -e "${CYAN}====================================================${NC}"
    echo -e "To compile native Velox on Linux, follow these steps:"
    echo ""
    echo -e "${YELLOW}1. Install system prerequisites (Ubuntu/Debian/Zorin OS):${NC}"
    echo "   sudo apt update && sudo apt install -y git python3 curl build-essential lsb-release"
    echo ""
    echo -e "${YELLOW}2. Install Google depot_tools:${NC}"
    echo "   git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git ~/depot_tools"
    echo "   export PATH=\"\$HOME/depot_tools:\$PATH\""
    echo ""
    echo -e "${YELLOW}3. Fetch Chromium 134 source code:${NC}"
    echo "   mkdir -p ~/velox-build && cd ~/velox-build"
    echo "   fetch --nohooks chromium"
    echo "   cd src && git checkout -b velox-134 refs/tags/134.0.6998.182"
    echo "   gclient sync -D"
    echo ""
    echo -e "${YELLOW}4. Clone Velox patches and apply them:${NC}"
    echo "   git clone https://github.com/okinamo-o/Velox.git ~/Velox"
    echo "   for p in ~/Velox/patches/*.patch; do patch -p1 -N < \"\$p\" || true; done"
    echo ""
    echo -e "${YELLOW}5. Configure GN args & Compile:${NC}"
    echo "   gn gen out/Release --args='is_debug=false is_component_build=false is_official_build=true symbol_level=0'"
    echo "   autoninja -C out/Release chrome"
    echo ""
    echo -e "${GREEN}[*] For full documentation, visit: https://github.com/okinamo-o/Velox${NC}"
}

# If script run with flags
if [ "$1" == "--wine" ] || [ "$1" == "-w" ]; then
    install_wine_runner
elif [ "$1" == "--update" ] || [ "$1" == "-u" ]; then
    update_velox_linux
elif [ "$1" == "--build" ] || [ "$1" == "-b" ]; then
    build_native_linux
else
    show_menu
fi
