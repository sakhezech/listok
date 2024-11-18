import os
import subprocess
import tempfile
import textwrap
from pathlib import Path

_COMMENT_STR = '#'


# TODO: add ability to pass in arguments for the editor
def editor_input(
    data: str = '',
    comment: str = '',
    filename: str = 'DEFAULT_FILENAME',
    editor: str | None = None,
) -> str:
    editor = editor or os.getenv('EDITOR') or os.getenv('VISUAL') or 'vi'
    comment = textwrap.dedent(comment)
    comment = '\n'.join(
        textwrap.wrap(
            comment,
            width=79,
            replace_whitespace=False,
            break_long_words=False,
            subsequent_indent='|   ',
        )
    )
    comment = textwrap.indent(comment, f'{_COMMENT_STR} ', lambda _: True)

    with tempfile.TemporaryDirectory() as tempdir_path:
        file_path = Path(tempdir_path) / filename
        file_path.write_text(f'{data}\n{comment}')

        subprocess.run([editor, str(file_path)])

        with file_path.open('r') as f:
            lines = f.readlines()
        res = ''.join(
            line.partition(_COMMENT_STR)[0] for line in lines
        ).strip()
        return res
