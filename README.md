# Octopus

**Human Action Execution Engine v0.1**

Octopus is a model-agnostic execution layer for Windows. It provides a safe, structured interface for external models to execute keyboard, mouse, and file operations.

## Project Structure

```text
Octopus/
├── core/
│   ├── executor/
│   │   └── human_executor.py     # Low-level I/O primitives
│   ├── agent.py                  # Main execution loop
│   ├── dispatcher.py             # Skill routing
│   └── model_adapter.py          # Input interface
├── skills/                       # Capability Modules
│   ├── mouse.py
│   ├── keyboard.py
│   ├── file.py
│   └── system.py
├── cli/
│   └── main.py                   # CLI Entry point
├── config/
│   └── config.yaml
├── logs/                         # Execution logs
├── workspace/                    # Sandboxed file area
├── install.ps1                   # One-click installer
├── run.ps1                       # Agent launcher
└── agent.ps1                     # CLI wrapper
```

## Installation

### PowerShell One-Liner

```powershell
irm https://raw.githubusercontent.com/abwoo/Octopus/main/install.ps1 | iex
```

### Manual Install

```powershell
git clone https://github.com/abwoo/Octopus.git
cd Octopus
pip install -r requirements.txt
```

## Usage

### Start Agent

Run the agent in listening mode (fetches actions from Adapter):

```powershell
.\run.ps1
```

### CLI Commands

Use `.\agent.ps1` (or `python cli/main.py`) to interact with the system:

```powershell
# General
.\agent.ps1 version      # Show version and system info
.\agent.ps1 status       # Check configuration and environment status
.\agent.ps1 update       # Update dependencies

# Execution
.\agent.ps1 run          # Start Agent Loop
.\agent.ps1 run '{"type":"mouse.position"}'  # Execute single action

# Configuration
.\agent.ps1 config show  # View all settings
.\agent.ps1 config set action_interval_ms 500

# Adapters
.\agent.ps1 model list   # List available adapters
.\agent.ps1 model use file  # Switch to file-based input

# Logs
.\agent.ps1 logs tail    # View recent logs
.\agent.ps1 logs clear   # Clear log file
```

## Skills API

### Mouse

- `mouse.move(x, y, duration=0.15)`
- `mouse.click(x, y, button="left")`
- `mouse.double_click(x, y)`
- `mouse.drag(x, y, duration=0.5, button="left")`
- `mouse.scroll(clicks)`
- `mouse.position()`

### Keyboard

- `keyboard.type(text, interval=0.02)`
- `keyboard.press(key)`
- `keyboard.hotkey(*keys)`

### File (Sandboxed)

- `file.read(path)`
- `file.write(path, content)`
- `file.append(path, content)`
- `file.list(path=".")`
- `file.delete(path)`
- `file.exists(path)`

### System

- `system.sleep(seconds)`
- `system.exit()`
- `system.screen_size()`
- `system.info()`

## Safety Mechanisms

1. **Emergency Stop**: Global hotkey **Ctrl+Alt+Q** immediately terminates the agent.
2. **Interval Check**: Enforced 300ms minimum delay between hardware actions.
3. **Coordinate Validation**: All mouse actions checked against screen bounds.
4. **Sandboxing**: File operations restricted to `workspace/` directory.

## Acknowledgments

This project references architecture patterns from **moltbot** and **agno** (MIT Licensed).

## License

MIT License
