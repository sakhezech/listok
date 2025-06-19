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
    parser.add_argument(
        '-^',
        '--above',
    )
    return parser


def make_sort_key_function(weights: dict[str, int]) -> Callable[[str], int]:
    sorted_weights = dict(
        sorted(weights.items(), key=lambda x: x[1], reverse=True)
    )

    def key_function(string: str) -> int:
        for kw, weight in sorted_weights.items():
            if kw.lower() in string.lower():
                return weight
        return 0

    return key_function


def to_int(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def cli(argv: Sequence[str] | None = None) -> None:
    config_path = Path('~/.config/listok/config.toml').expanduser()
    if not config_path.exists():
        config_path.parent.mkdir(parents=True)
        config_path.write_text('')
    config = Config(**tomllib.loads(config_path.read_text()))

    parser = make_parser()
    args = parser.parse_args(argv)

    key_function = make_sort_key_function(config.weights)
    if args.above is None:
        args.above = 0
    elif args.above in config.weights:
        args.above = config.weights[args.above]
    elif (val := to_int(args.above)) is not None:
        args.above = val
    else:
        raise ValueError(f'no such level: {args.above}')

    collected = get_todos(config)
    for project_name, todos in collected.items():
        filtered_todos = {
            k: v
            for k, v in todos.items()
            if args.filter.lower() in k.lower()
            and key_function(k) >= args.above
        }
        if filtered_todos:
            print(project_name)
            todo_names = list(filtered_todos.keys())
            todo_names.sort(
                key=key_function,
                reverse=True,
            )
            for todo_name in todo_names:
                print(f'    {todo_name}')


if __name__ == '__main__':
    cli(None)
