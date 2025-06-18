import dataclasses
from pathlib import Path


@dataclasses.dataclass
class Config:
    projects_dir: str = '~/Projects/'
    file_name: str = 'TODO.md'


def get_todos(config: Config) -> dict[str, dict[str, str]]:
    collected: dict[str, dict[str, str]] = {}
    for project_dir in Path(config.projects_dir).expanduser().iterdir():
        if not project_dir.is_dir():
            continue
        file = project_dir / config.file_name
        if not file.exists():
            continue

        project_todos: dict[str, list[str]] = {}
        project_name: str | None = None
        curr_todo: list[str] | None = None

        lines = file.read_text().splitlines()

        for line in lines:
            if line.startswith('##'):
                curr_todo = []
                title = line.removeprefix('##').strip()
                project_todos[title] = curr_todo
            elif line.startswith('#'):
                project_name = line.removeprefix('#').strip()
            elif curr_todo is not None:
                curr_todo.append(line)

        project_name = project_name if project_name else project_dir.name
        collected[project_name] = {
            k: '\n'.join(v).strip() for k, v in project_todos.items()
        }
    return collected
