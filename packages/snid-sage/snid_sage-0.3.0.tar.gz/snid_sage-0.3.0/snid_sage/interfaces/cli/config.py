"""
SNID Config Command
==================

Command for managing SNID configuration settings.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Dict, Any


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for the config command."""
    subparsers = parser.add_subparsers(
        dest="config_command", 
        help="Configuration commands",
        metavar="SUBCOMMAND"
    )
    
    # Show config command
    show_parser = subparsers.add_parser(
        'show', 
        help='Show current configuration'
    )
    show_parser.add_argument(
        '--format', 
        choices=['json', 'yaml', 'table'], 
        default='table',
        help='Output format'
    )
    
    # Set config command
    set_parser = subparsers.add_parser(
        'set', 
        help='Set configuration value'
    )
    set_parser.add_argument(
        'key', 
        help='Configuration key (e.g., templates.default_dir)'
    )
    set_parser.add_argument(
        'value', 
        help='Configuration value'
    )
    
    # Get config command
    get_parser = subparsers.add_parser(
        'get', 
        help='Get configuration value'
    )
    get_parser.add_argument(
        'key', 
        help='Configuration key'
    )
    
    # Reset config command
    reset_parser = subparsers.add_parser(
        'reset', 
        help='Reset configuration to defaults'
    )
    reset_parser.add_argument(
        '--confirm', 
        action='store_true',
        help='Confirm reset without prompting'
    )
    
    # Init config command
    init_parser = subparsers.add_parser(
        'init', 
        help='Initialize configuration file'
    )
    init_parser.add_argument(
        '--force', 
        action='store_true',
        help='Overwrite existing configuration'
    )


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    # Try user config directory first
    config_dir = Path.home() / '.config' / 'snid'
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / 'config.json'


def get_default_config() -> Dict[str, Any]:
    """Get default configuration values."""
    return {
        'templates': {
            'default_dir': str(Path.home() / 'templates'),
            'auto_detect': True
        },
        'analysis': {
            'zmin': -0.01,
            'zmax': 1.0,
            'rlapmin': 5.0,
            'lapmin': 0.3,
        
        },
        'preprocessing': {
            'aband_remove': False,
            'skyclip': False,
                    'savgol_window': 0,
        'savgol_fwhm': 0.0,
        'savgol_order': 3,
            'apodize_percent': 10.0
        },
        'output': {
            'default_dir': str(Path.home() / 'snid_results'),
            'save_plots': True,
            'save_results': True,
            'max_output_templates': 10
        },
        'llm': {
            'provider': 'openrouter',
            'model': 'openai/gpt-3.5-turbo',
            'api_key_file': str(Path.home() / '.config' / 'snid' / 'openrouter_key.txt')
        },
        'gui': {
            'theme': 'light',
            'window_size': [1200, 800],
            'auto_save_session': True
        }
    }


def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print(f"Warning: Could not load config from {config_path}, using defaults")
    
    return get_default_config()


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def get_nested_value(config: Dict[str, Any], key: str) -> Any:
    """Get a nested configuration value using dot notation."""
    keys = key.split('.')
    value = config
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            raise KeyError(f"Configuration key '{key}' not found")
    
    return value


def set_nested_value(config: Dict[str, Any], key: str, value: str) -> None:
    """Set a nested configuration value using dot notation."""
    keys = key.split('.')
    current = config
    
    # Navigate to the parent of the target key
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    # Convert value to appropriate type
    final_key = keys[-1]
    try:
        # Try to parse as JSON first (handles booleans, numbers, etc.)
        parsed_value = json.loads(value)
        current[final_key] = parsed_value
    except json.JSONDecodeError:
        # If that fails, treat as string
        current[final_key] = value


def format_config_table(config: Dict[str, Any], prefix: str = '') -> str:
    """Format configuration as a table."""
    lines = []
    
    for key, value in config.items():
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            lines.extend(format_config_table(value, full_key).split('\n'))
        else:
            lines.append(f"{full_key:<30} = {value}")
    
    return '\n'.join(lines)


def main(args: argparse.Namespace) -> int:
    """Main function for the config command."""
    try:
        if args.config_command == "show":
            config = load_config()
            
            if args.format == 'json':
                print(json.dumps(config, indent=2))
            elif args.format == 'yaml':
                try:
                    import yaml
                    print(yaml.dump(config, default_flow_style=False))
                except ImportError:
                    print("Error: PyYAML not installed. Use 'json' or 'table' format.", file=sys.stderr)
                    return 1
            else:  # table format
                print("SNID Configuration:")
                print("=" * 50)
                print(format_config_table(config))
            
            return 0
            
        elif args.config_command == "get":
            config = load_config()
            try:
                value = get_nested_value(config, args.key)
                print(value)
                return 0
            except KeyError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
                
        elif args.config_command == "set":
            config = load_config()
            try:
                set_nested_value(config, args.key, args.value)
                save_config(config)
                print(f"Set {args.key} = {args.value}")
                return 0
            except Exception as e:
                print(f"Error setting configuration: {e}", file=sys.stderr)
                return 1
                
        elif args.config_command == "reset":
            # Check if we're in a non-interactive environment (CI, etc.)
            import sys
            import os
            
            # Check multiple indicators of non-interactive environment
            is_noninteractive = (
                not sys.stdin.isatty() or  # Standard check
                os.environ.get('CI') or  # GitHub Actions, GitLab CI, etc.
                os.environ.get('GITHUB_ACTIONS') or  # GitHub Actions specific
                os.environ.get('RUNNER_OS') or  # GitHub Actions runner
                os.environ.get('SNID_NONINTERACTIVE')  # Manual override
            )
            
            if not args.confirm:
                if is_noninteractive:
                    print("Warning: Running in non-interactive environment. Use --confirm to reset configuration.")
                    return 1
                
                response = input("This will reset all configuration to defaults. Continue? (y/N): ")
                if response.lower() != 'y':
                    print("Reset cancelled.")
                    return 0
            
            config = get_default_config()
            save_config(config)
            print("Configuration reset to defaults.")
            return 0
            
        elif args.config_command == "init":
            config_path = get_config_path()
            
            if config_path.exists() and not args.force:
                print(f"Configuration file already exists at {config_path}")
                print("Use --force to overwrite.")
                return 1
            
            config = get_default_config()
            save_config(config)
            print(f"Configuration initialized at {config_path}")
            return 0
            
        else:
            print("Error: No config subcommand specified.", file=sys.stderr)
            print("Use 'snid config --help' for available commands.", file=sys.stderr)
            return 1
            
    except Exception as e:
        print(f"Error in config command: {e}", file=sys.stderr)
        return 1 