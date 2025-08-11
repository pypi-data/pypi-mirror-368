#!/usr/bin/env python3
"""
Kenning CLI - Main Command Interface and Entry Point

This module provides the primary command-line interface for Kenning, implementing a
user-friendly CLI that makes advanced AWS security and cost correlation analysis
accessible to DevOps engineers, SREs, and cloud architects.

The CLI follows the "command-subcommand" pattern popularized by tools like Git and
Docker, providing intuitive commands that match how users think about cloud risk
analysis workflows:

- `kenning scan` - Discover security and cost risks across AWS infrastructure
- `kenning explain` - Generate AI-powered explanations for compound risks
- `kenning report` - Create comprehensive analysis reports for sharing

Key Features:
    - Click-based command framework for professional CLI experience
    - Extensible command structure for adding new analysis capabilities
    - Consistent output formatting with emoji indicators for visual clarity
    - Demo mode support for testing and training without AWS credentials
    - Version management and help documentation built-in

Architecture:
    - Command group structure enables clean command organization
    - Each major command can be implemented in separate modules for maintainability
    - Consistent error handling and user feedback patterns
    - Integration points for core Kenning analysis engines

For detailed architectural explanation, see technical_docs/cli/main.md
"""

import click

# Import commands from separate modules
from .scan import scan
from .explain import explain
from .report import report
from .check_config import check_config


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Kenning CLI: An intelligent tool for contextual AWS cost and security co-optimization.

    This is the main entry point for Kenning's command-line interface. It implements
    a command group that organizes all of Kenning's functionality into logical
    subcommands that match user workflows.

    The function serves as both the root command and the command group coordinator,
    providing version information and serving as the parent for all subcommands.

    Usage:
        kenning --help          # Show all available commands
        kenning --version       # Show current version
        kenning scan --demo     # Run a demo security scan
        kenning explain --risk-id xyz  # Get AI explanation for specific risk
        kenning report --format pdf   # Generate analysis report
    """
    pass


# Add commands to the CLI group
cli.add_command(scan)
cli.add_command(explain)
cli.add_command(report)
cli.add_command(check_config)


if __name__ == "__main__":
    cli()
