# 🚀 Installation Guide

## Quick Start (Recommended)

**Easiest Method**: Use the included launcher

1. **Download** the repository
2. **Extract** to your desired location
3. **Double-click** `launcher.py`
4. **Play!** 🎮

The launcher will automatically:
- ✅ Check Python version (3.7+ required)
- ✅ Install pygame if missing
- ✅ Launch the game
- ✅ Handle all dependencies

---

## Manual Installation

### Prerequisites

- **Python 3.7+** (3.9+ recommended)
- **pip** (Python package manager)

### Step 1: Install Python

#### Windows
1. Download from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```powershell
   python --version
   ```

#### macOS
```bash
# Using Homebrew (recommended)
brew install python

# Or download from python.org
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Step 2: Install Dependencies

```bash
# Install pygame
pip install pygame

# Or install all at once
pip install -r requirements.txt
```

### Step 3: Run the Game

```bash
# Method 1: Direct execution
python aim.py

# Method 2: Using launcher
python launcher.py
```

---

## Installation Verification

### Check Installation
```bash
# Verify Python
python --version

# Verify pygame
python -c "import pygame; print(f'Pygame {pygame.version.ver} installed successfully!')"
```

### Expected Output
```
Python 3.x.x
Pygame 2.x.x installed successfully!
```

---

## Troubleshooting

### Common Issues

#### ❌ "Python is not recognized"
**Solution**: Add Python to PATH
- Windows: Reinstall Python with "Add to PATH" checked
- macOS/Linux: Add to shell profile

#### ❌ "No module named 'pygame'"
**Solution**: Install pygame
```bash
pip install pygame
```

#### ❌ "Permission denied"
**Solution**: Use user installation
```bash
pip install --user pygame
```

#### ❌ Game runs slowly
**Solutions**:
1. Close other applications
2. Update graphics drivers
3. Lower game resolution
4. Enable performance mode in settings

#### ❌ No sound
**Solutions**:
1. Check system volume
2. Verify audio device
3. Restart the game
4. Check in-game audio settings

### Advanced Troubleshooting

#### Virtual Environment (Recommended for developers)
```bash
# Create virtual environment
python -m venv aim_trainer_env

# Activate (Windows)
aim_trainer_env\Scripts\activate

# Activate (macOS/Linux)
source aim_trainer_env/bin/activate

# Install dependencies
pip install pygame

# Run game
python aim.py
```

#### Multiple Python Versions
```bash
# Use specific Python version
python3.9 aim.py
py -3.9 aim.py  # Windows
```

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 7+, macOS 10.12+, Linux (any modern distro)
- **Python**: 3.7+
- **RAM**: 512 MB
- **Storage**: 50 MB
- **Display**: 800x600 resolution

### Recommended Requirements
- **OS**: Windows 10+, macOS 11+, Ubuntu 20.04+
- **Python**: 3.9+
- **RAM**: 1 GB
- **Storage**: 100 MB
- **Display**: 1920x1080 resolution
- **Audio**: Sound card for background music

---

## Development Setup

### For Contributors

1. **Fork** the repository
2. **Clone** your fork
   ```bash
   git clone https://github.com/yourusername/elite-aim-trainer-pro.git
   cd elite-aim-trainer-pro
   ```
3. **Install** development dependencies
   ```bash
   pip install pygame
   ```
4. **Make** your changes
5. **Test** thoroughly
6. **Submit** a pull request

### Project Structure
```
elite-aim-trainer-pro/
├── aim.py              # Main game file
├── theme_manager.py    # Theme system
├── launcher.py         # Easy startup launcher
├── README.md          # Project documentation
├── CHANGELOG.md       # Version history
├── INSTALLATION.md    # This file
├── LICENSE           # MIT license
└── .gitignore        # Git ignore rules
```

---

## Updates

### Staying Updated
1. **Watch** the repository for notifications
2. **Check** CHANGELOG.md for new features
3. **Download** latest releases
4. **Backup** your settings before updating

### Manual Update
1. Download latest version
2. Extract to new folder
3. Copy settings from old installation
4. Delete old version

---

## Support

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/yourusername/elite-aim-trainer-pro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/elite-aim-trainer-pro/discussions)
- **Documentation**: Check README.md

### Reporting Bugs
1. Check existing issues first
2. Provide detailed description
3. Include system information
4. Add steps to reproduce
5. Attach error messages/screenshots

---

## Performance Tips

### Optimize Performance
- **Close** unnecessary applications
- **Update** graphics drivers
- **Use** performance mode
- **Lower** resolution if needed
- **Disable** fancy effects

### System Monitoring
- Monitor CPU/GPU usage
- Check available RAM
- Ensure stable frame rate
- Watch for overheating

---

## Next Steps

After successful installation:
1. 🎮 **Play** the tutorial mode
2. 🎨 **Customize** your theme
3. 🎯 **Adjust** crosshair style
4. 📊 **Track** your progress
5. 🏆 **Unlock** achievements

**Happy Training!** 🎯
