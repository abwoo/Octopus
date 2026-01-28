"""
Octopus CLI
===========
Command-line interface for Octopus v0.1.
Provides commands for running the agent, managing adapters, configuration, and logs.

Author: Octopus Contributors
License: MIT
"""

import os
import sys
import json
import logging
import subprocess
from typing import Optional

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import click
import yaml

from core.agent import Agent
from core.executor.human_executor import HumanExecutor
from core.dispatcher import Dispatcher

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

VERSION = "0.1.0"
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config", "config.yaml")
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, "workspace")
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "actions.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)


def load_config() -> dict:
    """Load configuration from YAML file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {
        "adapter": "mock",
        "workspace": "workspace",
        "log_file": "logs/actions.log",
        "action_interval_ms": 300,
    }


def save_config(config: dict) -> None:
    """Save configuration to YAML file."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f)


# ─────────────────────────────────────────────────────────────────────────────
# Output Helpers
# ─────────────────────────────────────────────────────────────────────────────

def echo_ok(msg: str) -> None:
    click.echo(click.style(f"[OK] {msg}", fg="green"))

def echo_err(msg: str) -> None:
    click.echo(click.style(f"[ERROR] {msg}", fg="red"))

def echo_info(msg: str) -> None:
    click.echo(click.style(f"[INFO] {msg}", fg="blue"))

def echo_header(title: str) -> None:
    click.echo(click.style(f"\n{'='*60}", fg="cyan"))
    click.echo(click.style(f"  {title}", fg="cyan", bold=True))
    click.echo(click.style(f"{'='*60}", fg="cyan"))


# ─────────────────────────────────────────────────────────────────────────────
# CLI Commands
# ─────────────────────────────────────────────────────────────────────────────

@click.group()
def cli():
    """Octopus - Human Action Execution Engine v0.1"""
    pass


@cli.command("version")
def cmd_version():
    """Display version information."""
    click.echo(f"  Octopus v{VERSION}")
    click.echo("  Human Action Execution Engine")
    try:
        import platform
        click.echo(f"  Python: {sys.version.split(' ')[0]}")
        click.echo(f"  System: {platform.system()} {platform.release()}")
    except:
        pass


@cli.command("status")
def cmd_status():
    """Display agent status and configuration."""
    config = load_config()
    echo_header("Octopus Status")
    
    # System Info
    try:
        executor = HumanExecutor(WORKSPACE_DIR)
        screen = executor.get_display_info()
        disp_str = f"{screen['width']}x{screen['height']}"
    except Exception as e:
        disp_str = f"Error: {e}"

    click.echo(click.style("Environment:", bold=True))
    click.echo(f"  Version:     {VERSION}")
    click.echo(f"  Display:     {disp_str}")
    click.echo(f"  Project:     {PROJECT_ROOT}")
    click.echo()

    click.echo(click.style("Configuration:", bold=True))
    click.echo(f"  Adapter:     {config.get('adapter', 'mock')}")
    click.echo(f"  Workspace:   {config.get('workspace', 'workspace')}")
    click.echo(f"  Log File:    {config.get('log_file', 'logs/actions.log')}")
    click.echo(f"  Interval:    {config.get('action_interval_ms', 300)} ms")
    click.echo()

    click.echo(click.style("Safety:", bold=True))
    click.echo("  Emergency:   Ctrl+Alt+Q")
    click.echo("  Sandboxed:   Yes")


@cli.command("run")
@click.argument("action_json", required=False)
@click.option("--debug", is_flag=True, help="Enable debug logging")
def cmd_run(action_json: Optional[str], debug: bool):
    """
    Run agent or execute a single action.

    \b
    Examples:
      agent run                              # Start agent loop
      agent run '{"type":"mouse.move"}'      # Execute single action
    """
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    config = load_config()
    
    # Override paths to absolute to ensure consistency
    config["workspace"] = os.path.abspath(os.path.join(PROJECT_ROOT, config.get("workspace", "workspace")))
    config["log_file"] = os.path.abspath(os.path.join(PROJECT_ROOT, config.get("log_file", "logs/actions.log")))

    if action_json:
        # Execute single action mode
        try:
            data = json.loads(action_json)
            # Support both list of actions and single action dict
            actions = data.get("actions", [data] if "type" in data else [])
        except json.JSONDecodeError as e:
            echo_err(f"Invalid JSON: {e}")
            return

        if not actions:
            echo_err("No valid actions found in JSON")
            return

        echo_info(f"Initializing executor in {config['workspace']}...")
        executor = HumanExecutor(config["workspace"])
        dispatcher = Dispatcher(executor)

        for action in actions:
            action_type = action.get("type", "unknown")
            echo_info(f"Executing: {action_type}")
            result = dispatcher.dispatch(action)
            
            if result.get("status") == "ok":
                msg = result.pop("message", "Done")
                result.pop("status", None)
                echo_ok(msg)
                if result:
                    for k, v in result.items():
                        click.echo(f"  {k}: {v}")
            else:
                echo_err(result.get("message", "Failed"))
    else:
        # Start Agent Loop
        echo_header("Starting Octopus Agent")
        click.echo("  Press Ctrl+Alt+Q for emergency stop")
        click.echo(f"  Listening for actions from '{config.get('adapter')}' adapter...")
        click.echo()

        try:
            agent = Agent(config)
            agent.start()
        except KeyboardInterrupt:
            echo_info("Stopped by user")
        except Exception as e:
            echo_err(f"Agent error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# Model/Adapter Management
# ─────────────────────────────────────────────────────────────────────────────

@cli.group("model")
def model_group():
    """Manage action providers (adapters)."""
    pass


@model_group.command("list")
def model_list():
    """List available adapters."""
    config = load_config()
    current = config.get("adapter", "mock")

    echo_header("Available Adapters")
    adapters = [
        ("mock", "Built-in test sequence for verification."),
        ("file", "Reads 'instruction.json' from workspace."),
    ]
    
    click.echo(f"{'  Name':<10} {'Description'}")
    click.echo(f"{'  ----':<10} {'-----------'}")
    
    for name, desc in adapters:
        marker = "* " if name == current else "  "
        click.echo(f"{marker}{name:<10} {desc}")
    click.echo()


@model_group.command("use")
@click.argument("name")
def model_use(name: str):
    """Switch to a different adapter (e.g., mock, file)."""
    valid = ["mock", "file"]
    name = name.lower()
    if name == "mockadapter": name = "mock"
    
    if name not in valid:
        echo_err(f"Unknown adapter: {name}")
        echo_info(f"Valid options: {', '.join(valid)}")
        return

    config = load_config()
    config["adapter"] = name
    save_config(config)
    echo_ok(f"Adapter set to: {name}")


# ─────────────────────────────────────────────────────────────────────────────
# Configuration Management
# ─────────────────────────────────────────────────────────────────────────────

@cli.group("config")
def config_group():
    """Manage configuration settings."""
    pass

@config_group.command("show")
def config_show():
    """Show current configuration."""
    config = load_config()
    echo_header("Current Configuration")
    for k, v in config.items():
        click.echo(f"  {k}: {v}")
    click.echo()

@config_group.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """
    Set a configuration value.
    
    Example:
      agent config set action_interval_ms 500
    """
    config = load_config()
    
    # Simple type inference
    if value.isdigit():
        value = int(value)
    elif value.lower() == "true":
        value = True
    elif value.lower() == "false":
        value = False
        
    config[key] = value
    save_config(config)
    echo_ok(f"Set '{key}' to '{value}'")


# ─────────────────────────────────────────────────────────────────────────────
# Logs Management
# ─────────────────────────────────────────────────────────────────────────────

@cli.group("logs")
def logs_group():
    """Manage execution logs."""
    pass

@logs_group.command("path")
def logs_path():
    """Show path to log file."""
    click.echo(LOG_FILE)

@logs_group.command("clear")
def logs_clear():
    """Clear the log file."""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            f.truncate(0)
        echo_ok("Logs cleared")
    else:
        echo_info("Log file does not exist")

@logs_group.command("tail")
@click.option("-n", "--lines", default=10, help="Number of lines to show")
def logs_tail(lines: int):
    """Show last N lines of log."""
    if not os.path.exists(LOG_FILE):
        echo_info("Log file is empty or missing")
        return
        
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.readlines()
            for line in content[-lines:]:
                click.echo(line.strip())
    except Exception as e:
        echo_err(f"Error reading logs: {e}")


@cli.command("update")
def cmd_update():
    """Update dependencies from requirements.txt."""
    echo_info("Updating dependencies...")
    req_file = os.path.join(PROJECT_ROOT, "requirements.txt")
    if os.path.exists(req_file):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", req_file, "-q"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                echo_ok("Dependencies updated successfully")
            else:
                echo_err("Update failed")
                click.echo(result.stderr)
        except Exception as e:
            echo_err(f"Update error: {e}")
    else:
        echo_err("requirements.txt not found")


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
