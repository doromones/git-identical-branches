#!/usr/bin/env sh
#
# A simple installation script for git-identical-branches on Linux/macOS.
#
# Usage:
#   ./install.sh
#
# This will copy git-identical-branches.py to /usr/local/bin/git-identical-branches
# (requires sudo for system-wide installation).
#
# Alternatively, you can manually place the script in your $PATH.
#

set -e

SCRIPT_NAME="git-identical-branches"
INSTALL_PATH="/usr/local/bin/${SCRIPT_NAME}"

echo "Copying to ${INSTALL_PATH} (sudo may prompt for password)..."
sudo cp git-identical-branches.py ${INSTALL_PATH}

echo "Making git-identical-branches.py executable..."
sudo chmod +x ${INSTALL_PATH}


echo "Installation complete. You can now use 'git identical-branches <subcommand>' or call it directly:"
echo "  ${SCRIPT_NAME} <subcommand>"