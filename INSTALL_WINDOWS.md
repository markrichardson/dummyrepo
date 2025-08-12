# Windows Installation Guide for DummyPy Educational Library

This guide provides step-by-step instructions for Windows users to set up the DummyPy educational library environment using Windows Subsystem for Linux (WSL) and Visual Studio Code. No prior Linux knowledge required.

## Prerequisites

- Windows 10 version 2004 and higher (Build 19041 and higher) or Windows 11
- Administrator access on your Windows machine
- Internet connection

## Step 1: Install Windows Subsystem for Linux (WSL)

### 1.1 Open PowerShell as Administrator

1. Press `Windows Key + R` to open the Run dialog
2. Type `powershell`
3. Right-click on "Windows PowerShell" and select "Run as administrator"
4. Click "Yes" when prompted by User Account Control

### 1.2 Install WSL

In the PowerShell window, run:
```powershell
wsl --install
```

This command will:
- Enable the required Windows features
- Install WSL2
- Install Ubuntu as the default Linux distribution
- You'll be prompted to restart your computer

### 1.3 Set Up Ubuntu (After Restart)

1. After restart, Ubuntu will automatically open
2. Wait for the installation to complete (this may take several minutes)
3. You'll be prompted to create a username and password:
   - Choose a simple username (e.g., your first name, all lowercase)
   - Choose a secure password
   - **Important**: Remember these credentials - you'll need them later

## Step 2: Install Visual Studio Code

### 2.1 Download and Install VS Code

1. Go to https://code.visualstudio.com/
2. Click "Download for Windows"
3. Run the downloaded installer
4. Follow the installation wizard (accept default settings)

### 2.2 Install Required VS Code Extensions

1. Open Visual Studio Code
2. Press `Ctrl+Shift+X` to open the Extensions panel
3. Install these essential extensions:
   - **WSL** (by Microsoft) - Search for "WSL" and install
   - **Python** (by Microsoft) - Search for "Python" and install

## Step 3: Set Up Your Development Environment

### 3.1 Connect VS Code to WSL

1. In VS Code, press `Ctrl+Shift+P` to open the Command Palette
2. Type "WSL: Connect to WSL" and press Enter
3. A new VS Code window will open connected to your Ubuntu environment
4. You should see "WSL: Ubuntu" in the bottom-left corner of VS Code

### 3.2 Open Terminal and Navigate

1. In the WSL-connected VS Code window, press `Ctrl+Shift+` ` (backtick) to open the terminal
2. You should see a Linux terminal prompt like: `username@computername:~$`
3. Create a projects directory:
   ```bash
   mkdir -p ~/code
   cd ~/code
   ```

## Step 4: Clone and Set Up DummyPy

### 4.1 Clone the Repository

**Note**: This requires syndicate access credentials

```bash
git clone git@github.com:[USERNAME]/dummypy.git
cd dummypy
```

### 4.2 Open Project in VS Code

```bash
code .
```

This opens the dummypy project in your current VS Code window.

### 4.3 Run Automated Setup

```bash
make setup
```

**What this does**:
- Installs the `uv` package manager
- Creates a Python virtual environment at `~/venvs/dummypy`
- Installs all project dependencies
- Sets up Jupyter kernel integration
- This process may take 5-10 minutes

## Step 5: Configure VS Code for Python Development

### 5.1 Select Python Interpreter

1. Press `Ctrl+Shift+P` to open Command Palette
2. Type "Python: Select Interpreter" and press Enter
3. Look for an interpreter path like: `/home/[your-username]/venvs/dummypy/bin/python`
4. If you don't see it:
   - Select "Enter interpreter path..."
   - Type: `/home/[your-username]/venvs/dummypy/bin/python` (replace `[your-username]` with your actual Ubuntu username)

## Step 6: Verify Your Setup

### 6.1 Test Basic Installation

```bash
make help
```
You should see a list of available commands.

### 6.2 Test Python Environment

```bash
make python
```
- This should start Python with the DummyPy environment
- You should see Python version 3.13.x
- Type `exit()` to quit Python

### 6.3 Test Jupyter Integration

1. Open a `.ipynb` file in the `notebooks/` folder
2. Click on the kernel selector in the top right of the notebook
3. You should see "DummyPy" as an available kernel
4. Select it and try running a simple cell

## Troubleshooting Common Issues

### "make: command not found"
**Problem**: The `make` command isn't available in Ubuntu.
**Solution**:
```bash
sudo apt update && sudo apt install make
```

### Git Authentication Issues
**Problem**: Git asks for credentials when cloning or shows "Permission denied (publickey)".
**Solution**: Set up SSH keys for GitHub:
```bash
# Generate SSH key (press Enter for default location, set a passphrase)
ssh-keygen -t ed25519 -C "your.email@company.com"

# Start SSH agent and add key
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key to clipboard (you'll need to add this to GitHub)
cat ~/.ssh/id_ed25519.pub
```
Then add the public key to your GitHub account: Settings → SSH and GPG keys → New SSH key

Alternatively, set up Git credentials:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"
```

### VS Code Can't Find Python Interpreter
**Problem**: VS Code shows "Python interpreter not found" or similar errors.
**Solution**:
- Make sure you're in a WSL window (check bottom-left corner shows "WSL: Ubuntu")
- Manually enter the interpreter path: `/home/[your-username]/venvs/dummypy/bin/python`

### Permission Denied Errors
**Problem**: Getting permission errors when running commands.
**Solution**:
- Make sure you're working in your home directory (`~/code/dummypy`)
- Don't use `sudo` unless specifically instructed

### WSL Ubuntu Won't Start
**Problem**: Ubuntu terminal shows errors or won't open.
**Solution**:
```powershell
# In PowerShell as Administrator
wsl --shutdown
wsl --unregister Ubuntu
wsl --install
```

### VS Code Extensions Not Working
**Problem**: Python or WSL extensions don't seem to work.
**Solution**:
- Make sure you installed extensions in the WSL window, not the regular Windows VS Code
- Try reloading the window: `Ctrl+Shift+P` → "Developer: Reload Window"

## Daily Workflow

Once everything is set up, your typical workflow will be:

1. **Open VS Code**
2. **Connect to WSL**: `Ctrl+Shift+P` → "WSL: Connect to WSL"
3. **Open your project**: `Ctrl+K, Ctrl+O` → Navigate to `/home/[username]/code/dummypy`
4. **Open terminal**: `Ctrl+Shift+` ` (backtick)
5. **Start coding!**

## Useful Commands Reference

| Command | Purpose |
|---------|---------|
| `make help` | Show all available commands |
| `make setup` | Set up/recreate the development environment |
| `make test` | Run the test suite |
| `make lint` | Check code quality |
| `make format` | Format code automatically |
| `make python` | Start Python in the virtual environment |
| `make clean` | Remove the virtual environment |

## Getting Help

If you run into issues not covered here:

1. Check that you're in the correct directory: `pwd` should show `/home/[username]/code/dummypy`
2. Verify your environment is active: `make info`
3. Try recreating the environment: `make clean && make setup`
4. Contact the development team via internal channels

---

**Note**: This guide assumes you're setting up on a clean Windows system. If you have existing WSL installations or development tools, some steps may differ.
