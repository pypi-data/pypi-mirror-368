from typing import Literal, Union
import subprocess
from importlib.resources import files
from portal_env.config import config
from pathlib import Path
import yaml


def read_env_name(yaml_path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    return data.get("name")


def get_micromamba_env_path(env_name: str, root_prefix=None) -> Union[Path, None]:
    query = ["micromamba", "env", "list", "--json"]
    if root_prefix is not None:
        query += [ "--root-prefix", root_prefix]
    try:
        result = subprocess.run(
            query,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        import json
        envs = json.loads(result.stdout)["envs"]
        for env in envs:
            suffix = Path('envs') / env_name
            if env.endswith(str(suffix)):
                return Path(env)
            
    except Exception as e:
        print("Error checking micromamba environments:", e)
        return None


def run_env(env_name: str, detach: bool, build_flag: bool, custom_path: Path):
    # Locate the path to the target env directory
    env_path = files("portal_env.envs").joinpath(env_name)
    pkg_path = files("portal_env")

    if custom_path is not None:
        path_prefix = custom_path
        micromamba_spec_path = custom_path / "spec.yml"
        env_main_path = custom_path / "env_main.py"
        assert micromamba_spec_path.exists() and env_main_path.exists(), "Custom path must contain spec.yml and env_main.py files"
    else:
        path_prefix = env_path
        micromamba_spec_path = env_path / "spec.yml"
        env_main_path = env_path / "env_main.py"
    env_setup_path = path_prefix / "env_setup.py"

    # Run micromamba create / update and run using that directory as the working dir
    micromamba_env_name = read_env_name(micromamba_spec_path)
    micromamba_env_path = get_micromamba_env_path(micromamba_env_name)
    if micromamba_env_path is None:
        print("Building micromamba env...")
        subprocess.run(["micromamba", "create", "-f", micromamba_spec_path.absolute(), "-y"], check=True)
        micromamba_env_path = get_micromamba_env_path(micromamba_env_name)
        assert micromamba_env_path is not None

        if env_setup_path.exists():
            subprocess.run(["micromamba", "run", "-n", micromamba_env_name, "python", env_setup_path], check=True)

    if build_flag:
        print('Updating micromamba env...')
        # "micromamba env update --file environment.yml --prune"
        subprocess.run(["micromamba", "env", "update", "--file", micromamba_spec_path.absolute(), "--prune"], check=True)

    # Run the server:
    run_args = [
        "micromamba", "run", "-n", micromamba_env_name, "python", env_main_path.absolute()
    ]
    run_args.append(micromamba_env_name)
    subprocess.run(run_args, cwd=str(pkg_path), check=True)
