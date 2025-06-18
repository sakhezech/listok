import argparse
from pathlib import Path
from typing import Sequence

import tomllib

from . import Config, get_todos
from .__version__ import __version__


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=__version__,
    )
    parser.add_argument(
        '-f',
        '--filter',
        default='',
    )
    return parser


def cli(argv: Sequence[str] | None = None) -> None:
    config_path = Path('~/.config/listok/config.toml').expanduser()
    if not config_path.exists():
        config_path.parent.mkdir(parents=True)
        config_path.write_text('')
    config = Config(**tomllib.loads(config_path.read_text()))

    parser = make_parser()
    args = parser.parse_args(argv)

    collected = get_todos(config)
    for project_name, todos in collected.items():
        filtered_todos = {k: v for k, v in todos.items() if args.filter in k}
        if filtered_todos:
            print(project_name)
            for todo_name, _ in filtered_todos.items():
                print(f'    {todo_name}')


if __name__ == '__main__':
    cli(None)
