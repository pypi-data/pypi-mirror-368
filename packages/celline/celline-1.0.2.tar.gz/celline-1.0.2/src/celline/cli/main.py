"""
Main CLI entry point for celline.
"""

import argparse
import sys
from typing import List, Optional

from celline.cli.commands import cmd_list, cmd_help, cmd_run, cmd_info, cmd_init, cmd_interactive, cmd_api, cmd_config, cmd_export, cmd_create


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog='celline',
        description='Celline - Single Cell Analysis Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new celline project')
    init_parser.add_argument('project_name', nargs='?', help='Project name')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new custom function template')
    create_parser.add_argument('function_name', help='Name of the function to create')
    create_parser.add_argument('--project-dir', '-p', default='.', help='Project directory (default: current directory)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all available functions')
    
    # Help command
    help_parser = subparsers.add_parser('help', help='Show help for a specific function')
    help_parser.add_argument('function_name', nargs='?', help='Function name to get help for')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a specific function')
    run_parser.add_argument('function_name', help='Function name to run')
    run_parser.add_argument('function_args', nargs='*', help='Arguments to pass to the function')
    run_parser.add_argument('--project-dir', '-p', default='.', help='Project directory (default: current directory)')
    run_parser.add_argument('--project-name', '-n', default='default', help='Project name (default: default)')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show system information')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configure celline settings')
    config_parser.add_argument('--system', choices=['multithreading', 'PBS'], help='Set execution system')
    config_parser.add_argument('--nthread', type=int, help='Set number of threads')
    config_parser.add_argument('--pbs-server', help='Set PBS server name (for PBS system)')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Launch interactive web interface')
    
    # API command (for testing)
    api_parser = subparsers.add_parser('api', help='Start API server only (for testing)')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data and reports')
    export_subparsers = export_parser.add_subparsers(dest='export_command', help='Export options')
    metareport_parser = export_subparsers.add_parser('metareport', help='Generate metadata report from samples.toml')
    metareport_parser.add_argument('--output', '-o', default='metadata_report.html', help='Output HTML file (default: metadata_report.html)')
    metareport_parser.add_argument('--project-dir', '-p', default='.', help='Project directory (default: current directory)')
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    
    if argv is None:
        argv = sys.argv[1:]
    
    # If no arguments provided, show help
    if not argv:
        parser.print_help()
        return 0
    
    # Quick exit for help/version commands (avoid heavy imports)
    if len(argv) >= 1 and argv[0] in ['--help', '-h', '--version', '-v']:
        args = parser.parse_args(argv)
        return 0
    
    args = parser.parse_args(argv)
    
    try:
        if args.command == 'init':
            cmd_init(args)
        elif args.command == 'create':
            cmd_create(args)
        elif args.command == 'list':
            cmd_list(args)
        elif args.command == 'help':
            cmd_help(args)
        elif args.command == 'run':
            # Check if the function is 'interactive'
            if hasattr(args, 'function_name') and args.function_name == 'interactive':
                cmd_interactive(args)
            else:
                cmd_run(args)
        elif args.command == 'info':
            cmd_info(args)
        elif args.command == 'config':
            cmd_config(args)
        elif args.command == 'interactive':
            cmd_interactive(args)
        elif args.command == 'api':
            cmd_api(args)
        elif args.command == 'export':
            cmd_export(args)
        else:
            parser.print_help()
            return 1
            
        return 0
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())