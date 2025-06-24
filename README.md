# Listok

Interproject note consolidator.

## Why?

There are too many projects to keep track of, sometimes I forget some exist.
If I consolidate all project notes in one place, I will stop forgetting about them.

## How?

Listok iterates through your projects (by default directories in `~/Projects/`) and searches for the note file (by default `NOTES.md`).
It then extracts markdown tasks as notes.

```markdown
# NOTES

Only the tasks matter, you can put here whatever you want.

- [x] add README (complete, will be skipped)
      you can put your note body here
      also they can be multiline
- [ ] add CI (incomplete, will be shown)
      just check code formatting for now, add test check later
- [ ] add tests (incomplete, will be shown)
```

## Usage

`listok` or `python3 -m listok`

```console
$ listok -h
usage: listok [-h] [-v] [-f SUBSTRING] [-^ LEVEL]

interproject note consolidator

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -f, --filter SUBSTRING
                        filter for notes with substring
  -^, --above LEVEL     filter for notes with priority level equal or above
```

Priority levels (`weights` in configuration) are a mapping of substrings to integers.
If the substring is in the name of the task, then the task gets that priority level.

## Configuration

The configuration file is at `~/.config/listok/config.toml`.

```toml
file_name = 'TODO.md' # default: 'NOTES.md'
projects_dir = '~/Work/' # default: '~/Projects/'

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
