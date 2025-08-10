import click
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


cli.add_command(scan)
cli.add_command(explain)
cli.add_command(report)
cli.add_command(check_config)
