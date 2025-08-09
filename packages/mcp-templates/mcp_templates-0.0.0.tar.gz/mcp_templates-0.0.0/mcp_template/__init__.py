"""
MCP Template Deployment Tool

A unified deployment system that provides:
- Rich CLI interface for standalone users
- Backend abstraction for different deployment targets
- Dynamic template discovery and configuration management
- Zero-configuration deployment experience

The system follows a layered architecture:
1. CLI Layer: Rich interface for user interaction
2. Management Layer: DeploymentManager orchestrates operations
3. Backend Layer: Pluggable deployment services (Docker, Kubernetes, etc.)
4. Discovery Layer: Dynamic template detection and configuration

Key Features:
- Template-driven configuration (no hardcoded template logic)
- Configurable image pulling (supports local development)
- Generic deployment utilities (reusable across templates)
- Comprehensive error handling and logging
"""

import argparse
import logging
import sys

from rich.console import Console

from mcp_template.backends.docker import DockerDeploymentService

# Import enhanced CLI modules
from mcp_template.cli import (
    EnhancedCLI,
    add_enhanced_cli_args,
    handle_enhanced_cli_commands,
)
from mcp_template.deployer import MCPDeployer
from mcp_template.manager import DeploymentManager
from mcp_template.template.utils.creation import TemplateCreator

# Import core classes that are used in CI and the CLI
from mcp_template.template.utils.discovery import TemplateDiscovery

# Export the classes for external use (CI compatibility)
__all__ = [
    "TemplateDiscovery",
    "DockerDeploymentService",
    "DeploymentManager",
    "MCPDeployer",
    "TemplateCreator",
]

# Constants
DEFAULT_CONFIG_PATH = "/config"
CUSTOM_NAME_HELP = "Custom container name"

console = Console()
logger = logging.getLogger(__name__)
enhanced_cli = EnhancedCLI()


def split_command_args(args):
    """
    Split command line arguments into a list, handling quoted strings.
    This is useful for parsing command line arguments that may contain spaces.
    """

    out_vars = {}
    for var in args:
        key, value = var.split("=", 1)
        out_vars[key] = value

    return out_vars


def main():
    """
    Main entry point for the MCP deployer CLI.
    """

    parser = argparse.ArgumentParser(
        description="Deploy MCP server templates with zero configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mcpt list                    # List available templates
  mcpt logs file-server        # View logs
  mcpt stop file-server        # Stop deployment
  mcpt shell file-server       # Open shell in container
  mcpt interactive            # Start interactive CLI
  mcpt> file-server             # Deploy file server with defaults
  mcpt> file-server --name fs   # Deploy with custom name
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List available templates",
        description="List all available templates with their metadata.",
    )
    list_parser.add_argument(
        "--deployed",
        action="store_true",
        help="List only deployed templates",
    )

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new template")
    create_parser.add_argument(
        "template_id", nargs="?", help="Template ID (e.g., 'my-api-server')"
    )
    create_parser.add_argument(
        "--config-file", help="Path to template configuration file"
    )
    create_parser.add_argument(
        "--non-interactive", action="store_true", help="Run in non-interactive mode"
    )

    # Deploy command (default)
    deploy_parser = subparsers.add_parser("deploy", help="Deploy a template")
    deploy_parser.add_argument("template", help="Template name to deploy")
    deploy_parser.add_argument("--name", help=CUSTOM_NAME_HELP)
    deploy_parser.add_argument("--data-dir", help="Custom data directory")
    deploy_parser.add_argument("--config-dir", help="Custom config directory")
    deploy_parser.add_argument(
        "--env", action="append", help="Environment variables (KEY=VALUE)"
    )
    deploy_parser.add_argument(
        "--config-file", help="Path to JSON/YAML configuration file"
    )
    deploy_parser.add_argument(
        "--config",
        action="append",
        help="Configuration values (KEY=VALUE) - for config_schema properties",
    )
    deploy_parser.add_argument(
        "--override",
        action="append",
        help="Template data overrides (KEY=VALUE) - supports double underscore notation (e.g., tools__0__custom_field=value)",
    )
    deploy_parser.add_argument(
        "--transport",
        choices=["http", "stdio", "sse", "streamable-http"],
        default=None,
        help="Transport protocol for MCP communication (default: http)",
    )
    deploy_parser.add_argument(
        "--port", type=int, default=7071, help="Port for HTTP transport (default: 7071)"
    )
    deploy_parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show available configuration options",
    )
    deploy_parser.add_argument(
        "--no-pull",
        action="store_true",
        help="Skip pulling Docker image (use local image)",
    )

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a deployed template")
    stop_parser.add_argument(
        "template",
        nargs="?",
        help="Template name to stop (optional if --name or --all is provided)",
    )
    stop_parser.add_argument("--name", help=CUSTOM_NAME_HELP)
    stop_parser.add_argument(
        "--all",
        action="store_true",
        help="Stop all deployments of this template or all templates if no template is specified",
    )

    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Show template logs")
    logs_parser.add_argument("template", help="Template name")
    logs_parser.add_argument("--name", help=CUSTOM_NAME_HELP)
    logs_parser.add_argument("-f", "--follow", action="store_true", help="Follow logs")

    # Shell command
    shell_parser = subparsers.add_parser("shell", help="Open shell in template")
    shell_parser.add_argument("template", help="Template name")
    shell_parser.add_argument("--name", help=CUSTOM_NAME_HELP)

    # Cleanup command
    cleanup_parser = subparsers.add_parser(
        "cleanup", help="Clean up stopped/failed deployments"
    )
    cleanup_parser.add_argument(
        "template", nargs="?", help="Template name to clean up (optional)"
    )
    cleanup_parser.add_argument(
        "--all", action="store_true", help="Clean up all deployments"
    )
    # Add enhanced CLI commands
    add_enhanced_cli_args(subparsers)

    # Parse arguments
    args = parser.parse_args()

    # Initialize deployer again if not already done
    if "deployer" not in locals():
        deployer = MCPDeployer()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if (
        (hasattr(args, "image") and args.image)
        and (hasattr(args, "template") and args.template)
        and (hasattr(args, "server_args") and not args.server_args)
    ):
        # Assume the user meant to pass this as server_args
        args.server_args = [args.template]
        args.template = None

    try:
        # Try enhanced CLI commands first, If the response is handled, return early
        if handle_enhanced_cli_commands(args):
            return

        if args.command == "list":
            deployer.list_templates(deployed_only=args.deployed)
        elif args.command == "create":
            creator = TemplateCreator()
            success = creator.create_template_interactive(
                template_id=getattr(args, "template_id", None),
                config_file=getattr(args, "config_file", None),
            )
            if not success:
                sys.exit(1)
        elif args.command == "deploy":
            template = args.template if hasattr(args, "template") else args.command

            # Show configuration options if requested
            if hasattr(args, "show_config") and args.show_config:
                deployer._show_config_options(template)
                return

            env_vars = (
                split_command_args(args.env)
                if hasattr(args, "env") and args.env
                else {}
            )
            config_values = (
                split_command_args(args.config)
                if hasattr(args, "config") and args.config
                else {}
            )
            override_values = (
                split_command_args(args.override)
                if hasattr(args, "override") and args.override
                else {}
            )

            # Deploy using enhanced CLI with transport support
            success = enhanced_cli.deploy_with_transport(
                template_name=template,
                transport=getattr(args, "transport", None),
                port=getattr(args, "port", 7071),
                data_dir=getattr(args, "data_dir", None),
                config_dir=getattr(args, "config_dir", None),
                env_vars=env_vars,
                config_file=getattr(args, "config_file", None),
                config_values=config_values,
                override_values=override_values,
                pull_image=not getattr(args, "no_pull", False),
            )
            if not success:
                sys.exit(1)
        elif args.command == "stop":
            # At least one of: template, --name, or --all must be provided
            if not (
                getattr(args, "template", None)
                or getattr(args, "name", None)
                or getattr(args, "all", False)
            ):
                console.print(
                    "[red]❌ You must provide at least one of: template, --name, or --all[/red]"
                )
                sys.exit(1)
            # If template is not provided, require --name or --all
            if not getattr(args, "template", None) and not (
                getattr(args, "name", None) or getattr(args, "all", False)
            ):
                console.print(
                    "[red]❌ You must provide either a template name, --name, or --all[/red]"
                )
                sys.exit(1)
            deployer.stop(
                getattr(args, "template", None),
                custom_name=getattr(args, "name", None),
                all_containers=getattr(args, "all", False),
            )
        elif args.command == "logs":
            deployer.logs(args.template, custom_name=getattr(args, "name", None))
        elif args.command == "shell":
            deployer.shell(args.template, custom_name=getattr(args, "name", None))
        elif args.command == "cleanup":
            deployer.cleanup(
                template_name=getattr(args, "template", None),
                all_containers=getattr(args, "all", False),
            )
        else:
            console.print(f"[red]❌ Unknown command: {args.command}[/red]")
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️  Operation cancelled[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
