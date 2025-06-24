import dataclasses
from pathlib import Path


@dataclasses.dataclass
class Config:
    projects_dir: str = '~/Projects/'
    file_name: str = 'NOTES.md'
    weights: dict[str, int] = dataclasses.field(default_factory=dict)


def get_notes(config: Config) -> dict[str, dict[str, str]]:
    collected: dict[str, dict[str, str]] = {}
    for project_dir in Path(config.projects_dir).expanduser().iterdir():
        if not project_dir.is_dir():
            continue
        file = project_dir / config.file_name
        if not file.exists():
            continue

        project_name = project_dir.name
        project_notes: dict[str, list[str]] = {}
        curr_note: list[str] | None = None

        lines = file.read_text().splitlines()

        for line in lines:
            if line.startswith('- [ ]'):
                curr_note = []
                title = line.removeprefix('- [ ]').strip()
                project_notes[title] = curr_note
            elif line.startswith('- [x]'):
                curr_note = None
            elif curr_note is not None:
                curr_note.append(line)

        collected[project_name] = {
            k: '\n'.join(v).strip() for k, v in project_notes.items()
        }
    return collected
