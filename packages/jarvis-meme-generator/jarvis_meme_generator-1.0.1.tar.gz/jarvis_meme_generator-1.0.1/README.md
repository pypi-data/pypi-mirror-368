# Jarvis Meme Generator

Generate custom Jarvis memes. This tool takes the image below and overlays your text in the white region.

![Example](static/jarvis.png)

## Features

- 🎨 **Smart Text Rendering**: Automatically wraps and resizes text to fit perfectly
- 💪 **Bold Text**: Uses bold fonts and rendering techniques for maximum impact  
- 🔄 **Auto-Sizing**: Dynamically adjusts font size to ensure all text fits
- 📱 **Cross-Platform**: Works on Windows, macOS, and Linux
- ⚡ **Simple CLI**: Just one command to generate your meme

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install jarvis-meme-generator
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/jbejjani2022/jarvis-meme-generator.git
cd jarvis-meme-generator

# Install with pip
pip install .
```

## Usage

After installation, you can use the `jarvis` command from anywhere:

```bash
jarvis "Your text here"
```

### Examples

```bash
# Simple text
jarvis "Hello World"

# Longer text (automatically wrapped)
jarvis "This is a longer message that will be automatically wrapped to multiple lines"
```

Generated images are saved to `~/jarvis/` by default.

### Custom Output Directory

```bash
jarvis "Your text" -o /path/to/output/directory
```

## Requirements

- Python 3.7 or higher
- Pillow (PIL) library (automatically installed)

## How It Works

1. Takes your input text
2. Loads the base Jarvis image
3. Intelligently wraps text to fit the white area
4. Auto-adjusts font size if needed
5. Renders bold text for maximum readability
6. Saves the result with a filename based on your text

## Output

Images are saved as `jarvis_YOUR_TEXT_HERE.png` in the specified directory (default: `~/jarvis/`).

## Troubleshooting

### Command not found: jarvis

If you get "command not found" after installation, you may need to add `~/.local/bin` to your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Or for zsh:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Font Issues

The tool automatically tries to find the best available bold font on your system. If you're having font rendering issues, make sure you have system fonts installed.

## License

MIT License - feel free to use and modify.

## Contributing

Pull requests welcome! Feel free to add features, fix bugs, or improve the documentation.