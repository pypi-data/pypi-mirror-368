"""
CLI tool for automatically generating the docker files and running the env portal
"""
from typing import Literal
import click
from pathlib import Path

supported_envs_aliases = {
    "atari": "ale",
}
supported_envs = [
    "ale",
    "mujoco",
    "retro",
    "craftium",
]


@click.command()
@click.argument("env_name")
@click.option("-d", "--detach", is_flag=True, help="Run the Docker container in detached mode")
@click.option("--backend", type=click.Choice(['docker', 'micromamba']), default='docker')
@click.option("-b", "--build", is_flag=True, help="Run the Docker container in detached mode")
@click.option("-p", "--path", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
              help="Path to a directory containing custom Dockerfile.env and env_main.py files.")
def start(
    env_name: str, 
    detach: bool, 
    backend: Literal['docker', 'micromamba'], 
    build: bool, 
    path: Path = None
):
    if env_name in supported_envs_aliases:
        env_name = supported_envs_aliases[env_name]
    if env_name not in supported_envs and path is None:
        raise ValueError(f"Unsupported env name: {env_name}")
    
    if backend == 'docker':
        from portal_env.docker_backend import run_env
        run_env(env_name, detach, build_flag=build, custom_path=path)
    elif backend == 'micromamba':
        from portal_env.micromamba_backend import run_env
        run_env(env_name, detach, build_flag=build, custom_path=path)


@click.command()
@click.argument("env_name")
def stop(env_name: str):
    pass


@click.group()
def main():
    pass


main.add_command(start)


if __name__ == '__main__':
    main()