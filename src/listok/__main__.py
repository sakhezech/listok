import argparse
import textwrap
from collections.abc import Iterable, Sequence
from pathlib import Path
from sqlite3 import Connection
from typing import NoReturn

import platformdirs

from .input import editor_input
from .models import Note, Tag
from .orm import create_connection

_SPLIT = '\n\n'


def print_and_exit(*message: str, exit_code: int = 1) -> NoReturn:
    import sys

    print(*message, file=sys.stderr)
    exit(exit_code)


def make_tag_set(tags: Iterable[str]) -> set[str]:
    tag_set = set(tags)
    if '.' in tag_set:
        tag_set.remove('.')
        tag_set.add(Path.cwd().name)
    return tag_set


def str_to_note_components(string: str) -> tuple[str, str, set[str]]:
    sections = string.split(_SPLIT)
    head, *body_parts, tagline = sections
    body = _SPLIT.join(body_parts)
    tags = make_tag_set(tagline.split())
    return head, body, tags


def note_components_to_str(head: str, body: str, tags: Iterable[str]) -> str:
    tagline = ' '.join(tags)
    return _SPLIT.join([head, *[v for v in (body, tagline) if v]])


def add_func(tags: list[str], m: str | None, conn: Connection, **_) -> None:
    head = m
    body = ''
    tags_ = make_tag_set(tags)

    if not head:
        data = note_components_to_str('', '', tags_)
        comment = f"""\
            Existing tags: {' '.join(tag.tag_id for tag in Tag.all(conn))}
            vim:ft=conf
        """
        res = editor_input(
            data=data,
            comment=comment,
            filename='ADD_NOTE',
        )
        if not res:
            print_and_exit('empty message, aborted')
        try:
            head, body, tags_ = str_to_note_components(res)
        except ValueError:
            print_and_exit('empty message, aborted')

    note = Note(head=head, body=body).save(conn)
    note.add_tags(conn, tags_)
    conn.commit()
    print(f'{note.short_id} {note.head}')


def edit_func(id: str, conn: Connection, **_) -> None:
    note = Note.by_partial_id(conn, id)
    if not note:
        print_and_exit(f'no notes found: {id}')

    tags = [tag.tag_id for tag in note.get_tags(conn)]
    res = editor_input(
        data=note_components_to_str(note.head, note.body, tags),
        comment=f"""\
            Editing note {note.short_id} {note.head}
            vim:ft=conf
        """,
        filename='EDIT_NOTE',
    )
    try:
        note.head, note.body, tags = str_to_note_components(res)
    except ValueError:
        print_and_exit('empty message, aborted')
    note.save(conn)
    note.update_tags(conn, tags)
    conn.commit()
    print(f'{note.short_id} {note.head}')


def list_func(
    tags: list[str], not_: list[str] | None, conn: Connection, **_
) -> None:
    in_tags = make_tag_set(tags)
    out_tags = make_tag_set(not_) if not_ else []

    notes = Note.by_tags(conn, list(in_tags), list(out_tags))
    for note in notes:
        print(
            note.short_id,
            note.head,
            # HACK: arbitrary not thought out width value
            textwrap.shorten(note.body, width=70),
        )


def cli(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser('listok')
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser('add')
    add_parser.set_defaults(func=add_func)
    add_parser.add_argument('-m')
    add_parser.add_argument('tags', nargs='*')

    edit_parser = subparsers.add_parser('edit')
    edit_parser.set_defaults(func=edit_func)
    edit_parser.add_argument('id')

    list_parser = subparsers.add_parser('list')
    list_parser.set_defaults(func=list_func)
    list_parser.add_argument('tags', nargs='*')
    list_parser.add_argument('-n', '--not', nargs='*', dest='not_')

    # ---
    listok_dirs = platformdirs.PlatformDirs('listok')
    listok_dirs.user_data_path.mkdir(parents=True, exist_ok=True)
    db_path = listok_dirs.user_data_path / 'listki.sqlite3'

    args = parser.parse_args(argv)
    conn = create_connection(db_path)
    args.func(**args.__dict__, conn=conn)


if __name__ == '__main__':
    cli()
