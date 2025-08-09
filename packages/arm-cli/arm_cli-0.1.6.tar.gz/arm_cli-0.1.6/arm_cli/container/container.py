import subprocess

import click
import docker
import inquirer


@click.group()
def container():
    """Basic tools for managing Docker containers. For more extensive tooling, try lazydocker"""
    pass


def get_running_containers():
    """Retrieve a list of running Docker containers"""
    client = docker.from_env()
    return client.containers.list(filters={"status": "running"})


@container.command("list")
def list_containers():
    """List all Docker containers"""
    containers = get_running_containers()

    if containers:
        for container in containers:
            print(f"{container.id[:12]}: {container.name}")
    else:
        print("No running containers found.")


@container.command("attach")
def attach_container():
    """Interactively select a running Docker container and attach to it"""
    containers = get_running_containers()

    if not containers:
        print("No running containers found.")
        return

    container_choices = [
        inquirer.List(
            "container",
            message="Select a container to attach to",
            choices=[f"{container.name} ({container.id[:12]})" for container in containers],
            carousel=True,
        )
    ]

    answers = inquirer.prompt(container_choices)
    selected_container_name = answers["container"].split(" ")[0]  # Extract container name

    print(f"Attaching to {selected_container_name}...")

    try:
        subprocess.run(["docker", "exec", "-it", selected_container_name, "/bin/bash"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error attaching to container: {e}")
    except KeyboardInterrupt:
        print("\nExiting interactive session...")


@container.command("restart")
def restart_container():
    """Interactively select a running Docker container and restart it"""
    containers = get_running_containers()

    if not containers:
        print("No running containers found.")
        return

    container_choices = [
        inquirer.List(
            "container",
            message="Select a container to restart",
            choices=[f"{container.name} ({container.id[:12]})" for container in containers],
            carousel=True,
        )
    ]

    answers = inquirer.prompt(container_choices)
    if not answers:
        print("No container selected.")
        return

    selected_container_name = answers["container"].split(" ")[0]

    print(f"Restarting {selected_container_name}...")

    try:
        client = docker.from_env()
        container = client.containers.get(selected_container_name)
        container.restart()
        print(f"Container {selected_container_name} restarted successfully.")
    except docker.errors.NotFound:
        print(f"Error: Container {selected_container_name} not found.")
    except docker.errors.APIError as e:
        print(f"Error restarting container: {e}")


@container.command("stop")
def stop_container():
    """Interactively select a running Docker container and stop it"""
    containers = get_running_containers()

    if not containers:
        print("No running containers found.")
        return

    container_choices = [
        inquirer.List(
            "container",
            message="Select a container to stop",
            choices=[f"{container.name} ({container.id[:12]})" for container in containers],
            carousel=True,
        )
    ]

    answers = inquirer.prompt(container_choices)
    if not answers:
        print("No container selected.")
        return

    selected_container_name = answers["container"].split(" ")[0]  # Extract container name

    print(f"Stopping {selected_container_name}...")

    try:
        client = docker.from_env()
        container = client.containers.get(selected_container_name)
        container.stop()
        print(f"Container {selected_container_name} stopped successfully.")
    except docker.errors.NotFound:
        print(f"Error: Container {selected_container_name} not found.")
    except docker.errors.APIError as e:
        print(f"Error stopping container: {e}")
