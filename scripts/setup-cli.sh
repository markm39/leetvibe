#!/bin/bash
#
# Auto-setup LeetVibe CLI on first plugin load
# Called by SessionStart hook
#

BIN_DIR="$HOME/.local/bin"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
MARKER="$HOME/.leetvibe/.cli-installed"

# Skip if already set up
if [ -f "$MARKER" ] && command -v leetvibe &> /dev/null; then
    exit 0
fi

# Create bin directory
mkdir -p "$BIN_DIR"
mkdir -p "$HOME/.leetvibe"

# Create symlink
ln -sf "$PLUGIN_ROOT/bin/leetvibe" "$BIN_DIR/leetvibe"
chmod +x "$PLUGIN_ROOT/bin/leetvibe"

# Add to PATH in shell config if needed
add_to_path() {
    local shell_rc="$1"
    if [ -f "$shell_rc" ]; then
        if ! grep -q "# LeetVibe CLI" "$shell_rc" 2>/dev/null; then
            echo "" >> "$shell_rc"
            echo "# LeetVibe CLI" >> "$shell_rc"
            echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$shell_rc"
        fi
    fi
}

# Try both shell configs
add_to_path "$HOME/.zshrc"
add_to_path "$HOME/.bashrc"

# Mark as installed
touch "$MARKER"

# Output message for Claude to show user
echo "LeetVibe CLI installed to $BIN_DIR/leetvibe"
echo "Run 'source ~/.zshrc' or restart terminal to use 'leetvibe' command"
