import dataclasses
import datetime
import os
from sqlite3 import Connection
from typing import Annotated, Self

from .orm import Junction, Model


def _gen_random_id() -> str:
    # emulating git commit ids
    return os.urandom(20).hex()


class Note(Model):
    note_id: str = dataclasses.field(default_factory=_gen_random_id)
    creation_date: datetime.datetime = dataclasses.field(
        default_factory=datetime.datetime.now
    )
    head: str
    body: str = ''

    @classmethod
    def by_id(cls, conn: Connection, id_: str) -> Self | None:
        res = conn.execute(
            f""" SELECT * FROM {Note} WHERE {Note.note_id} = ?;
            """,
            (id_,),
        ).fetchone()
        return cls(**res) if res else None

    @classmethod
    def by_partial_id(cls, conn: Connection, partial_id: str) -> Self | None:
        res = conn.execute(
            f""" SELECT * FROM {Note} WHERE {Note.note_id} LIKE ?;
            """,
            (partial_id + '%',),
        ).fetchone()
        return cls(**res) if res else None

    @classmethod
    def by_tags(
        cls,
        conn: Connection,
        in_tags: list[str] | None = None,
        out_tags: list[str] | None = None,
    ) -> list[Self]:
        if in_tags is None:
            in_tags = []
        if out_tags is None:
            out_tags = []
        in_params = ','.join(['?'] * len(in_tags))
        out_params = ','.join(['?'] * len(out_tags))
        res = conn.execute(
            f""" SELECT {Note}.*
                 FROM {Note}
                 JOIN {NoteTag} ON {Note.note_id} = {NoteTag.note_id}
                 GROUP BY {Note.note_id}
                 HAVING
                     SUM({NoteTag.tag_id} IN ({in_params})) = {len(in_tags)}
                     AND
                     SUM({NoteTag.tag_id} IN ({out_params})) = 0;
            """,
            in_tags + out_tags,
        ).fetchall()
        return [cls(**row) for row in res]


class Tag(Model):
    tag_id: str
    description: str

    @classmethod
    def by_id(cls, conn: Connection, tag_id: str) -> Self | None:
        res = conn.execute(
            f""" SELECT * FROM {Tag} WHERE {Tag.tag_id} = ?;
            """,
            (tag_id,),
        ).fetchone()
        return cls(**res) if res else None


class NoteTag(Junction):
    __table_name__ = 'note_tag'
    note_id: Annotated[str, Note]
    tag_id: Annotated[str, Tag]
