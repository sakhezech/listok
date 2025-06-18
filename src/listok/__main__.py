import argparse
from collections.abc import Callable
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


def make_sort_key_function(weights: dict[str, int]) -> Callable[[str], int]:
    def key_function(string: str) -> int:
        for kw, weight in weights.items():
            if kw in string:
                return weight
        return 0

    return key_function


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
            todo_names = list(filtered_todos.keys())
            todo_names.sort(
                key=make_sort_key_function(config.weights),
                reverse=True,
            )
            for todo_name in todo_names:
                print(f'    {todo_name}')


if __name__ == '__main__':
    cli(None)
