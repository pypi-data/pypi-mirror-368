#!/bin/bash

echo "Installing Jarvis Meme Generator..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Install the package
pip3 install --user .

echo "Installation complete!"
echo ""
echo "You can now run: jarvis \"Your text here\""
echo "Images will be saved to ~/jarvis/"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "WARNING: ~/.local/bin is not in your PATH."
    echo "Add this line to your ~/.bashrc or ~/.zshrc:"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Then restart your terminal or run: source ~/.bashrc"
fi