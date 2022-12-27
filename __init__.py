import os
import click
import json
from subprocess import Popen
from typing import Dict, List

from dotenv import dotenv_values

FILES = [
    '.env.shared',
    '.env.shared.{env}',
    '.env',
    '.env.{env}',
]

def load_values_from_files(env, filter_unknown=False):
    files = [x.format(env=env) for x in FILES]

    dotenv_as_dict = {}
    for file in files:
        if os.path.isfile(file):
            dotenv_as_dict.update(dotenv_values(file))

    if filter_unknown:
        dotenv_as_dict.update({k: os.environ.get(k) for k, v in dotenv_as_dict.items() if k in os.environ})
    else:
        dotenv_as_dict.update(os.environ)

    return dotenv_as_dict

def load_env_from_files(env: str) -> None:
    dotenv_as_dict = load_values_from_files(env)

    for key, value in dotenv_as_dict.items():
        os.environ[key] = value

@click.command(context_settings=dict(ignore_unknown_options=True))
@click.option('--env', envvar='ENV', required=True, help="Environment to use e.g. dev, staging, prod. You can also set this from ENV environment variable.")
@click.option('--dump', nargs=1, default=False, help="Outputs the env as json to stdout. Variables not declared in the input files are ignored.")
@click.argument('command', nargs=-1, type=click.UNPROCESSED)
def main(env: str, command: List[str], dump) -> None:
    
    if dump:
        print(json.dumps(load_values_from_files(env, True), indent=4))
        exit(0)

    if not command:
        click.echo('No command given.')
        exit(1)

    exit(_run_command(command, load_values_from_files(env)))

def _run_command(command: List[str], env: Dict[str, str]) -> int:
    cmd_env = os.environ.copy()
    cmd_env.update(env)

    p = Popen(command,
              universal_newlines=True,
              bufsize=0,
              shell=False,
              env=cmd_env)
    _, _ = p.communicate()

    return p.returncode


