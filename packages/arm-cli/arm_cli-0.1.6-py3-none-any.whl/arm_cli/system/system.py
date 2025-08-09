import subprocess

import click
import docker
import inquirer

from arm_cli.system.setup_utils import (
    setup_data_directories,
    setup_docker_group,
    setup_shell,
    setup_xhost,
)


@click.group()
def system():
    """Manage the system this CLI is running on"""
    pass


@system.command()
@click.option("-f", "--force", is_flag=True, help="Skip confirmation prompts")
def setup(force):
    """Generic setup (will be refined later)"""

    setup_xhost(force=force)

    setup_shell(force=force)

    # Setup docker group (may require sudo)
    if not setup_docker_group(force=force):
        print("Docker group setup was not completed.")
        print("You can run this setup again later with: arm-cli system setup")

    # Setup data directories (may require sudo)
    if not setup_data_directories(force=force):
        print("Data directory setup was not completed.")
        print("You can run this setup again later with: arm-cli system setup")

    # Additional setup code can go here (e.g., starting containers, attaching, etc.)
    pass
