# pckgr 📦

A comprehensive Python package management tool that simplifies the entire development workflow from initialization to deployment.

## 📑 Table of Contents

1. [Features](#-features)
2. [Requirements](#-requirements)
3. [Installation](#-installation)
   - 3.1 [Install Python 3.8+](#step-1-install-python-38)
   - 3.2 [Install pckgr System-Wide](#step-2-install-pckgr-system-wide)
   - 3.3 [Set Up GitHub Integration](#step-3-set-up-github-integration)
4. [Quick Start](#-quick-start)
   - 4.1 [Initialize a New Package](#initialize-a-new-package)
   - 4.2 [Multi-Repository Management](#multi-repository-management)
5. [Command Reference](#-command-reference)
   - 5.1 [Package Management](#package-management)
   - 5.2 [Version Control](#version-control)
   - 5.3 [Development Tools](#development-tools)
   - 5.4 [Configuration](#configuration)
6. [Advanced Configuration](#-advanced-configuration)
   - 6.1 [Global Settings](#global-settings)
   - 6.2 [Git Configuration](#git-configuration)
   - 6.3 [Package Aliases](#package-aliases)
7. [Error Handling](#-error-handling)
8. [Multi-Repository Workflow](#-multi-repository-workflow)
9. [Troubleshooting](#-troubleshooting)
   - 9.1 [Common Issues](#common-issues)
   - 9.2 [Debug Mode](#debug-mode)
10. [License](#-license)
11. [Contributing](#-contributing)
12. [Support](#-support)
13. [Examples](#-examples)
    - 13.1 [Basic Package Development](#basic-package-development)
    - 13.2 [Multi-Project Management](#multi-project-management)
    - 13.3 [Development Workflow](#development-workflow)

## ✨ Features

- **🚀 Quick Package Initialization**: Set up new Python packages with all necessary files
- **📋 Smart Dependency Management**: Automatically detect and manage project dependencies
- **🔄 Multi-Repository Operations**: Bulk push/pull operations across multiple git repositories
- **🛠️ Development Tools**: TODO scanning, code statistics, and mini-games
- **⚙️ Configuration Management**: Advanced git and build system configuration
- **🎯 Interactive CLI**: User-friendly prompts with validation and error handling

## 📋 Requirements

- **Python 3.8 or higher**
- **Git** (for version control operations)
- **GitHub CLI (gh)** (for seamless GitHub integration)
- **SSH keys configured with GitHub** (recommended for secure authentication)
- **Internet connection** (for package installation and GitHub operations)

## 🔧 Installation

### Step 1: Install Python 3.8+

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### macOS
```bash
# Using Homebrew (recommended)
brew install python@3.8

# Or download from python.org
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.8 python3.8-pip python3.8-venv
```

#### Linux (CentOS/RHEL/Fedora)
```bash
# Fedora
sudo dnf install python3.8 python3.8-pip

# CentOS/RHEL (requires EPEL)
sudo yum install python3.8 python3.8-pip
```

### Step 2: Install pckgr System-Wide

**⚠️ Important**: Install pckgr system-wide (not in a virtual environment) to enable `pckgr init` to work from any directory.

```bash
# Install from PyPI (recommended)
pip install pckgr

# Or install from GitHub (latest development version)
pip install git+https://github.com/HiDrNikki/pckgr.git
```

**Verify Installation:**
```bash
pckgr --help
```

### Step 3: Set Up GitHub Integration

pckgr is designed to work seamlessly with GitHub. Follow these steps to set up proper authentication:

#### Install GitHub CLI
```bash
# Windows (using winget)
winget install --id GitHub.cli

# Windows (using Chocolatey)
choco install gh

# macOS (using Homebrew)
brew install gh

# Linux (Ubuntu/Debian)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Linux (CentOS/RHEL/Fedora)
sudo dnf install gh
```

#### Authenticate with GitHub
```bash
# Login to GitHub (opens browser for authentication)
gh auth login

# Choose:
# - GitHub.com
# - HTTPS or SSH (recommend SSH for better security)
# - Authenticate via web browser
```

#### Set Up SSH Keys (Recommended)
```bash
# Generate SSH key (replace with your email)
ssh-keygen -t ed25519 -C "your.email@example.com"

# Start SSH agent
# Windows (PowerShell)
Start-Service ssh-agent
ssh-add ~/.ssh/id_ed25519

# macOS/Linux
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Add SSH key to GitHub (automatically)
gh ssh-key add ~/.ssh/id_ed25519.pub --title "My Development Machine"

# Test SSH connection
ssh -T git@github.com
```

#### Configure Git
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global user.github "your-github-username"

# Set default branch name
git config --global init.defaultBranch main

# Optional: Enable signed commits (if you have GPG set up)
git config --global commit.gpgsign true
```

## 🚀 Quick Start

### Initialize a New Package
```bash
mkdir new-package
cd new-package
pckgr init
```

This will:
- Create package structure (`src/`, `tests/`, etc.)
- Generate `pyproject.toml` with your details
- Set up virtual environment
- Initialize git repository
- Install detected dependencies

### Multi-Repository Management
```bash
# From a directory containing multiple git repositories
cd /path/to/projects

# Push all repositories with changes
pckgr push --all -m "Update all projects"

# Interactive push (choose individual repositories)
pckgr push -m "Selective updates"

# Skip dependency updates for faster operation
pckgr push --skip-deps --all -m "Quick push"
```

## 📚 Command Reference

### Package Management

#### `pckgr init`
Initialize a new Python package in the current directory.

```bash
pckgr init                    # Interactive setup
pckgr init --pull             # Pull from existing repository
```

**What it does:**
- Creates standard Python package structure
- Generates `pyproject.toml` with metadata
- Sets up virtual environment
- Detects and installs dependencies
- Initializes git repository
- Creates initial commit

#### `pckgr build`
Build and optionally upload the package.

```bash
pckgr build                             # Build only (minor version bump)
pckgr build --patch                     # Build with patch version bump
pckgr build --major                     # Build with major version bump
pckgr build --version "1.2.3"          # Build with specific version
pckgr build --upload                    # Build and upload to PyPI
pckgr build --test-pypi                 # Upload to Test PyPI
pckgr build --version "2.0.0" --upload # Set version and upload
```

### Version Control

#### `pckgr push`
Commit and push changes to git repository.

```bash
pckgr push -m "Commit message"              # Basic push
pckgr push -m "Message" --tag               # Push with tags
pckgr push --all -m "Message"               # Multi-repo: push all
pckgr push --skip-deps -m "Message"         # Skip dependency updates
pckgr push --dry-run -m "Message"           # Preview without changes
pckgr push --version "1.2.3" -m "Message"  # Set specific version before push
```

**Multi-Repository Features:**
- Automatically detects git repositories in subdirectories
- Only shows repositories with uncommitted changes
- Interactive or bulk push modes
- Continues on errors with user choice
- Smart dependency updates per repository
- **Note**: `--version` flag not available for multi-repository pushes

#### `pckgr pull`
Pull latest changes from git repository.

```bash
pckgr pull                    # Pull from default branch
pckgr pull -b develop         # Pull from specific branch
pckgr pull -r upstream        # Pull from specific remote
```

#### `pckgr patch`
Apply patch files from `.pckgr/patches/`.

```bash
pckgr patch                   # Apply all patches
```

### Development Tools

#### `pckgr tools`
Various development utilities and mini-tools.

```bash
# TODO Management
pckgr tools --todo                          # Scan for TODO items
pckgr tools --todo --priority               # Include priority parsing
pckgr tools --todo --tags todo,fixme        # Filter by tags
pckgr tools --todo --group-by priority      # Group by priority
pckgr tools --todo --group-by tag           # Group by tag type

# Code Statistics
pckgr tools --stats                         # Show code statistics

# Dependency Management
pckgr tools --update-dependencies           # Update dependencies
```

**TODO Scanner Features:**
- Supports: `TODO`, `FIXME`, `HACK`, `XXX`, `NOTE`, `WARNING`, `BUG`
- Priority parsing: `(HIGH)`, `[CRITICAL]`, `!!!`
- Multiple comment styles: `#`, `//`, `/* */`, `<!-- -->`
- Grouping and filtering options

### Configuration

#### `pckgr config`
Manage pckgr and git configuration.

```bash
pckgr config --show          # Show current config
pckgr config --init          # Initialize with defaults
```

**Configuration Features:**
- Git remote management
- Custom build backends
- Upload targets (PyPI, Test PyPI)
- Command flags and hooks
- Author information storage

#### `pckgr tree`
Display project directory structure (respects `.gitignore`).

```bash
pckgr tree                    # Show project tree
```

#### `pckgr help`
Show help information.

```bash
pckgr help                    # General help
pckgr <command> --help        # Command-specific help
```

## ⚙️ Advanced Configuration

### Global Settings
pckgr stores global settings in `module_settings.json`:

```json
{
  "global": {
    "author": {
      "name": "Your Name",
      "email": "your.email@example.com", 
      "github": "your-username"
    },
    "default_license": "MIT",
    "python_requires": ">=3.8"
  },
  "performance": {
    "max_parallel_processes": 4,
    "enable_parallel_processing": true
  }
}
```

### Git Configuration
Project-specific git settings in `.pckgr/settings.json`:

```json
{
  "git": {
    "default_remote": "origin",
    "default_branch": "main",
    "remotes": {
      "origin": {"url": "...", "type": "github"},
      "upstream": {"url": "...", "type": "github"}
    },
    "commands": {
      "push_flags": [],
      "pull_flags": [],
      "commit_flags": ["-S"]
    }
  }
}
```

### Package Aliases
Common package name mappings for dependency detection:

```json
{
  "common_aliases": {
    "cv2": "opencv-python",
    "PIL": "Pillow", 
    "sklearn": "scikit-learn",
    "bs4": "beautifulsoup4"
  }
}
```

## 🔍 Error Handling

pckgr uses numbered error codes for structured error handling:

- **100-199**: File system errors
- **200-299**: Git/version control errors  
- **300-399**: Package management errors
- **400-499**: Configuration errors
- **500-599**: User input errors
- **1000+**: Soft errors (warnings)

## 🤝 Multi-Repository Workflow

Perfect for managing multiple projects:

```bash
# Directory structure
/projects/
  ├── project-a/     (git repo)
  ├── project-b/     (git repo)  
  ├── project-c/     (git repo)
  └── other-files

# From /projects/ directory
pckgr push --all -m "Update all projects"
```

**Features:**
- Only processes repositories with changes
- Interactive or automatic mode
- Continues on individual failures
- Per-project dependency updates
- Progress tracking and summaries

## 🐛 Troubleshooting

### Common Issues

**1. "Command not found" after installation**
```bash
# Ensure Python scripts directory is in PATH
# Windows: Add %APPDATA%\Python\Python38\Scripts to PATH
# macOS/Linux: Add ~/.local/bin to PATH
```

**2. "Permission denied" errors**
```bash
# Use --user flag for user installation
pip install --user git+https://github.com/HiDrNikki/pckgr.git
```

**3. Dependency update hanging**
```bash
# Skip dependency updates
pckgr push --skip-deps -m "Message"
```

**4. Virtual environment issues**
```bash
# Ensure pckgr is installed globally, not in venv
pip list | grep pckgr
```

**5. GitHub authentication issues**
```bash
# Check if you're logged in
gh auth status

# Re-authenticate if needed
gh auth login

# Test SSH connection
ssh -T git@github.com
# Should show: "Hi username! You've successfully authenticated..."
```

**6. SSH key problems**
```bash
# List SSH keys added to GitHub
gh ssh-key list

# Add existing SSH key
gh ssh-key add ~/.ssh/id_ed25519.pub

# Generate new SSH key if needed
ssh-keygen -t ed25519 -C "your.email@example.com"
```

**7. Git remote issues**
```bash
# Check current remotes
git remote -v

# Switch from HTTPS to SSH (if needed)
git remote set-url origin git@github.com:username/repository.git
```

### Debug Mode
```bash
# Enable verbose output (if implemented)
pckgr --verbose <command>
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/HiDrNikki/pckgr/issues)
- **Email**: [littler.compression@gmail.com](mailto:littler.compression@gmail.com)
- **Documentation**: This README and `pckgr --help`

## 🎯 Examples

### Basic Package Development
```bash
# Create new package
mkdir my-package && cd my-package
pckgr init

# Develop your code...
# src/my_package/main.py

# Commit and push
pckgr push -m "Initial implementation"

# Build and upload
pckgr build --upload
```

### Multi-Project Management
```bash
# From directory with multiple projects
pckgr push --all -m "Weekly updates"

# Interactive mode
pckgr push -m "Selective updates"
# Choose: [i]ndividual/[a]ll/[c]ancel: i
# Push repository 'project-a'? (y/N): y
```

### Development Workflow
```bash
# Check TODOs before committing
pckgr tools --todo --priority

# Update dependencies
pckgr tools --update-dependencies

# Quick stats
pckgr tools --stats

# Push with clean dependencies
pckgr push -m "Clean update"
```

---

**pckgr** - Making Python package management simple and efficient! 🚀