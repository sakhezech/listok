# Listok

Interproject info consolidator.

## Why?

There are too many projects to keep track of, sometimes I forget some exist.
If I consolidate all project ideas and TODOs in one place, I will stop forgetting about them.

## How?

Listok iterates through your projects (by default directories in `~/Projects/`) and searches for the TODO file (by default `TODO.md`).
It then extracts markdown tasks as todos.

```markdown
# TODOs

Only the tasks matter, you can put here whatever you want.

- [x] add README (complete, will be skipped)
      hello world, hello world
- [ ] add CI (incomplete, will be shown)
      just check code formatting for now, add test check later
- [ ] add tests (incomplete, will be shown)
```

## Usage

`listok` or `python3 -m listok`

```console
$ listok -h
usage: listok [-h] [-v] [-f FILTER] [-^ ABOVE]

options:
  -h, --help           show this help message and exit
  -v, --version        show program's version number and exit
  -f, --filter FILTER
  -^, --above ABOVE
```

- `--filter` will filter for todos with the provided substring.
- `--above` will filter for todos with the priority level equal or above the provided.

Priority levels (`weights` in configuration) are a mapping of substrings to integers.
If the substring is in the name of the task, then the task gets that priority level.

## Configuration

The configuration file is at `~/.config/listok/config.toml`.

```toml
file_name = 'TODO.md' # default: 'TODO.md'
projects_dir = '~/Projects/' # default: '~/Projects/'

[weights] # default: {}
critical = 100
high = 75
medium = 50
low = 25
none = 0
```

## Development

Use `fate format` to format your code.

To get started:

```sh
git clone https://github.com/sakhezech/listok
cd listok
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```
