#!/bin/bash
#
# LeetVibe Installer
#
# Quick install:
#   curl -fsSL https://raw.githubusercontent.com/markm39/leetvibe/main/install.sh | bash
#
# Or clone and run:
#   git clone https://github.com/markm39/leetvibe.git
#   cd leetvibe && ./install.sh
#

set -e

REPO="markm39/leetvibe"
INSTALL_DIR="$HOME/.leetvibe-plugin"
BIN_DIR="$HOME/.local/bin"

echo ""
echo "  LeetVibe Installer"
echo "  =================="
echo ""

# Check for required dependencies
check_deps() {
    local missing=()

    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    fi

    if ! command -v claude &> /dev/null; then
        missing+=("claude (Claude Code CLI)")
    fi

    if [ ${#missing[@]} -ne 0 ]; then
        echo "  Missing dependencies: ${missing[*]}"
        echo "  Please install them first."
        exit 1
    fi

    echo "  [OK] Dependencies found"
}

# Download or update the plugin
download_plugin() {
    if [ -d "$INSTALL_DIR" ]; then
        echo "  [OK] Updating existing installation..."
        cd "$INSTALL_DIR"
        git pull --quiet origin main
    else
        echo "  [OK] Downloading LeetVibe..."
        git clone --quiet "https://github.com/$REPO.git" "$INSTALL_DIR"
    fi
}

# Set up the CLI
setup_cli() {
    mkdir -p "$BIN_DIR"

    # Create symlink to leetvibe CLI
    ln -sf "$INSTALL_DIR/bin/leetvibe" "$BIN_DIR/leetvibe"
    chmod +x "$INSTALL_DIR/bin/leetvibe"

    # Make scripts executable
    chmod +x "$INSTALL_DIR/scripts/"*.py 2>/dev/null || true

    echo "  [OK] CLI installed to $BIN_DIR/leetvibe"
}

# Add to PATH if needed
setup_path() {
    local shell_rc=""

    if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
        shell_rc="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ] || [ -f "$HOME/.bashrc" ]; then
        shell_rc="$HOME/.bashrc"
    fi

    if [ -n "$shell_rc" ]; then
        if ! grep -q "$BIN_DIR" "$shell_rc" 2>/dev/null; then
            echo "" >> "$shell_rc"
            echo "# LeetVibe CLI" >> "$shell_rc"
            echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$shell_rc"
            echo "  [OK] Added $BIN_DIR to PATH in $shell_rc"
        fi
    fi
}

# Create shell alias for easy plugin loading
setup_alias() {
    local shell_rc=""

    if [ -f "$HOME/.zshrc" ]; then
        shell_rc="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        shell_rc="$HOME/.bashrc"
    fi

    if [ -n "$shell_rc" ]; then
        if ! grep -q "leetvibe-claude" "$shell_rc" 2>/dev/null; then
            echo "" >> "$shell_rc"
            echo "# Start Claude Code with LeetVibe plugin" >> "$shell_rc"
            echo "alias leetvibe-claude='claude --plugin-dir $INSTALL_DIR'" >> "$shell_rc"
            echo "  [OK] Created alias 'leetvibe-claude' in $shell_rc"
        fi
    fi
}

# Main installation
main() {
    check_deps
    download_plugin
    setup_cli
    setup_path
    setup_alias

    echo ""
    echo "  Installation complete!"
    echo ""
    echo "  To get started:"
    echo ""
    echo "    1. Restart your terminal (or run: source ~/.zshrc)"
    echo ""
    echo "    2. Start Claude with LeetVibe:"
    echo "       $ leetvibe-claude"
    echo "       # or: claude --plugin-dir $INSTALL_DIR"
    echo ""
    echo "    3. Code normally - quizzes auto-generate when new concepts appear"
    echo ""
    echo "    4. Solve quizzes and submit from terminal:"
    echo "       $ leetvibe list"
    echo "       $ leetvibe submit 001"
    echo ""
}

main "$@"
